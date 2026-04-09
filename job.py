from typing import Optional
from dataclasses import dataclass

@dataclass
class Job:
    title: str
    url: str
    text: Optional[str]
    searched_via: str
    low_quality: bool = False