from typing import Optional
from dataclasses import dataclass
from datetime import date

@dataclass
class Job:
    title: str
    url: str
    text: Optional[str]
    searched_via: str
    low_quality: bool = False
    keep: Optional[bool] = None
    score: Optional[int] = None
    reason: str = ""
    is_ai_role: Optional[bool] = None
    manual_check_required: bool = False
    date: Optional[str] = None