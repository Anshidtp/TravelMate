from fastapi import APIRouter, HTTPException, Depends
from .models import TravelRequest, TravelResponse
from .services.agent import TravelPlannerGraph
from .config import get_settings

router = APIRouter()

@router.post("/api/plan", response_model=TravelResponse)
async def create_travel_plan(
    request: TravelRequest,
    settings=Depends(get_settings)
):
    try:
        graph = TravelPlannerGraph()
        state = graph.process_request({
            "destination": request.destination,
            "dates": request.dates,
            "preferences": request.preferences or ""
        })
        
        return TravelResponse(
            itinerary=state["itinerary"],
            plan=state["plan"],
            events=[event for event in state["content"] if event]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))