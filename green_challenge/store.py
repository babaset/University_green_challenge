

from __future__ import annotations

import hashlib
import os
import random
from datetime import datetime
from pathlib import Path

from .constants import ECO_ACTIONS
from .models import Claim, PendingRequest, Student
from .persistence import DEFAULT_DATA_FILE, load_challenge_data, save_challenge_data


class ChallengeStore:
   

    def __init__(self, data_file: Path | None = None):
        self.data_file = data_file or DEFAULT_DATA_FILE
        self.students, self.pending_requests, self.next_request_id = load_challenge_data(self.data_file)

    def register_student(self, name: str, student_id: str) -> Student:
        
        clean_name = " ".join(name.split())
        clean_id = student_id.strip().upper()

        if not clean_name:
            raise ValueError("Please enter a student name.")
        if not clean_id:
            raise ValueError("Please enter a student ID.")
        if clean_id in self.students:
            raise ValueError("That student ID is already registered.")

        student = Student(student_id=clean_id, name=clean_name)
        self.students[clean_id] = student
        self._save()
        return student

    def submit_claim(
        self,
        student_id: str,
        action: str,
        evidence_path: str,
        evidence_description: str,
    ) -> Claim:
        
        student = self.students.get(student_id)
        if student is None:
            raise ValueError("Please sign in as a registered student to submit a claim.")
        if action not in ECO_ACTIONS:
            raise ValueError("Please select an eco-action.")

        evidence_hash = self._hash_evidence(evidence_path)
        if self._evidence_has_been_used(evidence_hash):
            raise ValueError(
                "This photo has already been used as evidence for another claim. "
                "Please upload a new, original photo."
            )

        request_id = str(self.next_request_id)
        self.next_request_id += 1
        extra_scrutiny = self._requires_extra_scrutiny(student.trust_score)
        claim = Claim(
            action=action,
            points=ECO_ACTIONS[action],
            status="Pending Review",
            request_id=request_id,
            review_level="Extra scrutiny" if extra_scrutiny else "Standard review",
            evidence_path=evidence_path,
            evidence_description=evidence_description,
            evidence_hash=evidence_hash,
            created_at=self._timestamp(),
        )
        student.claims_log.append(claim)
        self.pending_requests.append(PendingRequest(request_id, student_id, claim))
        self._save()
        return claim

    def review_claim(self, request_id: str, decision: str, admin_note: str = "") -> tuple[Student, Claim]:
        """Approve or reject one pending claim, exactly once."""
        request = self.get_pending_request(request_id)
        if request is None:
            raise ValueError("That request is no longer pending.")

        student = self.students.get(request.student_id)
        if student is None:
            self.pending_requests.remove(request)
            raise LookupError("This student's record no longer exists, so the request was removed.")

        claim = request.claim
        clean_note = " ".join(admin_note.split())
        if decision == "approve":
            student.points += claim.points
            student.trust_score = min(100, student.trust_score + 5)
            claim.status = "Admin-Approved"
        elif decision == "reject":
            student.trust_score = max(0, student.trust_score - 20)
            claim.status = "Rejected"
        else:
            raise ValueError("Unknown review decision.")

        if clean_note:
            claim.admin_note = clean_note
        claim.reviewed_at = self._timestamp()
        self.pending_requests.remove(request)
        self._save()
        return student, claim

    def update_pending_status(self, request_id: str, status: str, admin_note: str = "") -> Claim:
        """Add a non-final review status without changing points or trust."""
        if status not in {"Under Review", "Needs More Evidence"}:
            raise ValueError("Unknown pending review status.")

        request = self.get_pending_request(request_id)
        if request is None:
            raise ValueError("That request is no longer pending.")

        clean_note = " ".join(admin_note.split())
        request.claim.status = status
        if clean_note:
            request.claim.admin_note = clean_note
        self._save()
        return request.claim

    def delete_pending_claim(self, request_id: str) -> Claim:
        
        request = self.get_pending_request(request_id)
        if request is None:
            raise ValueError("That request is no longer pending.")

        student = self.students.get(request.student_id)
        if student is None:
            self.pending_requests.remove(request)
            self._save()
            raise LookupError("This student's record no longer exists, so the request was removed.")

        student.claims_log.remove(request.claim)
        self.pending_requests.remove(request)
        self._save()
        return request.claim

    def delete_approved_claim(self, student_id: str, request_id: str) -> Claim:
        """Delete an approved claim and reverse only its awarded points."""
        student = self.students.get(student_id)
        if student is None:
            raise ValueError("That student record no longer exists.")

        claim = next((item for item in student.claims_log if item.request_id == request_id), None)
        if claim is None:
            raise ValueError("That claim no longer exists in the student's history.")
        if claim.status not in {"Admin-Approved", "Auto-Approved"}:
            raise ValueError("Only approved claims can be deleted from claim history.")

        student.points = max(0, student.points - claim.points)
        student.claims_log.remove(claim)
        self._save()
        return claim

    def get_pending_request(self, request_id: str) -> PendingRequest | None:
        """Find a request that is still awaiting review."""
        return next((item for item in self.pending_requests if item.request_id == request_id), None)

    def get_leaderboard(self) -> list[Student]:
        """Sort by points, trust, name, then ID for stable ties."""
        return sorted(
            self.students.values(),
            key=lambda student: (
                -student.points,
                -student.trust_score,
                student.name.casefold(),
                student.student_id.casefold(),
            ),
        )

    def _save(self) -> None:
        """Persist the current challenge state after a successful change."""
        save_challenge_data(
            self.data_file,
            self.students,
            self.pending_requests,
            self.next_request_id,
        )

    @staticmethod
    def _timestamp() -> str:
        """Return a local, readable timestamp for claim history."""
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def _requires_extra_scrutiny(trust_score: int) -> bool:
        """Decide whether a claim needs extra checking based on trust."""
        if trust_score >= 80:
            probability = 0.10
        elif trust_score >= 50:
            probability = 0.30
        elif trust_score >= 20:
            probability = 0.60
        else:
            probability = 1.00
        return random.random() < probability

    @staticmethod
    def _hash_evidence(evidence_path: str) -> str:
        """Return a stable SHA-256 fingerprint for the uploaded image bytes."""
        digest = hashlib.sha256()
        try:
            with open(evidence_path, "rb") as evidence_file:
                for block in iter(lambda: evidence_file.read(1024 * 1024), b""):
                    digest.update(block)
        except OSError as error:
            raise ValueError("The selected photo could not be read. Please choose it again.") from error
        return digest.hexdigest()

    def _evidence_has_been_used(self, evidence_hash: str) -> bool:
        """Check every historical claim, including rejected ones, for one image."""
        for student in self.students.values():
            for claim in student.claims_log:
                known_hash = claim.evidence_hash
                if not known_hash and os.path.isfile(claim.evidence_path):
                    try:
                        known_hash = self._hash_evidence(claim.evidence_path)
                    except ValueError:
                        continue
                    claim.evidence_hash = known_hash
                if known_hash == evidence_hash:
                    return True
        return False
