"""Data structures for students and their eco-action claims."""

from dataclasses import dataclass, field


@dataclass
class Claim:
    """One eco-action submitted by a student for administrator review."""

    action: str
    points: int
    status: str
    request_id: str
    review_level: str
    evidence_path: str
    evidence_description: str
    evidence_hash: str = ""
    created_at: str = ""
    reviewed_at: str = ""
    admin_note: str = ""


@dataclass
class Student:
    """A registered student and their sustainability record."""

    student_id: str
    name: str
    points: int = 0
    trust_score: int = 100
    claims_log: list[Claim] = field(default_factory=list)


@dataclass
class PendingRequest:
    """A claim waiting for an administrator's decision."""

    request_id: str
    student_id: str
    claim: Claim
