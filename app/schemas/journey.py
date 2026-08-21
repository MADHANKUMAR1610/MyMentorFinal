from pydantic import BaseModel
from typing import List


class JourneyItem(BaseModel):
    key: str
    title: str
    description: str
    done: bool
    icon: str


class JourneyResponse(BaseModel):
    journey: List[JourneyItem]