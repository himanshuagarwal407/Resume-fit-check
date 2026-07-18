from pydantic import BaseModel
from typing import List

class ScanResponse(BaseModel):
    """The structured result returned to the frontend after scanning a resume against a JD."""

    match_score: int    #0-100
    matched_keywords: List[str]  #List of keywords matched in the resume
    missing_keywords: List[str]  #List of keywords missing in the resume
    formatting_warnings: List[str]  #List of formatting warnings in the resume
    summary: str  #Short human readable verdict