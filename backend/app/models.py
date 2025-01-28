from typing import TypedDict, List, Optional
from pydantic import BaseModel

class TravelRequest(BaseModel):
    destination: str
    dates: str
    preferences: Optional[str] = None

class TravelResponse(BaseModel):
    itinerary: str
    plan: str
    events: List[str]

class State(TypedDict):
    destination: str
    dates: str
    preferences: str
    plan: str
    content: List[str]
    itinerary: str