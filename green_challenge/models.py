

from dataclasses import dataclass, field


@dataclass
class Claim:
    

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
   

    student_id: str
    name: str
    points: int = 0
    trust_score: int = 100
    claims_log: list[Claim] = field(default_factory=list)


@dataclass
class PendingRequest:


    request_id: str
    student_id: str
    claim: Claim
