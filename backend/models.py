from pydantic import BaseModel
from typing import List, Optional


class ExperienceMatch(BaseModel):
    required_experience: str  # e.g., "5-12 years"
    candidate_experience: str  # e.g., "2 years"
    meets_requirement: bool
    reasoning: str


class ScanResponse(BaseModel):
    """The structured result returned to the frontend after scanning a resume against a JD."""
    match_score: int  # 0-100
    experience_match: ExperienceMatch
    strong_matches: List[str]  # skills demonstrated with real context/usage
    weak_matches: List[str]    # skills only listed, no demonstrated usage
    missing_keywords: List[str]
    formatting_warnings: List[str]
    summary: str