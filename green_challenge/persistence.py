"""Read and write challenge data in a JSON file.

The JSON file is intentionally human-readable, so it is easy to inspect or
back up. It is kept outside the Python package, beside the start-up script.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import Claim, PendingRequest, Student


DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "green_challenge_data.json"


def load_challenge_data(data_file: Path) -> tuple[dict[str, Student], list[PendingRequest], int]:
    """Load students and pending requests, or return an empty challenge."""
    if not data_file.exists():
        return {}, [], 1

    try:
        with data_file.open("r", encoding="utf-8") as file:
            saved_data = json.load(file)

        students: dict[str, Student] = {}
        claims_by_request_id: dict[str, tuple[str, Claim]] = {}
        for saved_student in saved_data.get("students", []):
            student_id = str(saved_student["student_id"])
            claims = []
            for saved_claim in saved_student.get("claims_log", []):
                claim = Claim(
                    action=str(saved_claim["action"]),
                    points=int(saved_claim["points"]),
                    status=str(saved_claim["status"]),
                    request_id=str(saved_claim["request_id"]),
                    review_level=str(saved_claim["review_level"]),
                    evidence_path=str(saved_claim["evidence_path"]),
                    evidence_description=str(saved_claim["evidence_description"]),
                    evidence_hash=str(saved_claim.get("evidence_hash", "")),
                    created_at=str(saved_claim.get("created_at", "")),
                    reviewed_at=str(saved_claim.get("reviewed_at", "")),
                    admin_note=str(saved_claim.get("admin_note", "")),
                )
                claims.append(claim)
                claims_by_request_id[claim.request_id] = (student_id, claim)

            students[student_id] = Student(
                student_id=student_id,
                name=str(saved_student["name"]),
                points=int(saved_student.get("points", 0)),
                trust_score=int(saved_student.get("trust_score", 100)),
                claims_log=claims,
            )

        pending_requests = []
        for request_id in saved_data.get("pending_request_ids", []):
            saved_request = claims_by_request_id.get(str(request_id))
            if saved_request is not None:
                student_id, claim = saved_request
                pending_requests.append(PendingRequest(claim.request_id, student_id, claim))

        next_request_id = int(saved_data.get("next_request_id", 1))
        return students, pending_requests, max(1, next_request_id)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not load saved data from {data_file.name}: {error}") from error


def save_challenge_data(
    data_file: Path,
    students: dict[str, Student],
    pending_requests: list[PendingRequest],
    next_request_id: int,
) -> None:
    """Save all records safely, replacing the data file only when complete."""
    saved_data = {
        "students": [asdict(student) for student in students.values()],
        "pending_request_ids": [request.request_id for request in pending_requests],
        "next_request_id": next_request_id,
    }
    temporary_file = data_file.with_suffix(".tmp")
    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(saved_data, file, ensure_ascii=False, indent=2)
        temporary_file.replace(data_file)
    except OSError as error:
        raise OSError(f"Could not save data to {data_file.name}: {error}") from error
