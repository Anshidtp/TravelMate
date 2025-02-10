from fastapi import APIRouter, HTTPException, Depends
from .models import TravelRequest, TravelResponse
from .services.agent import TravelPlannerGraph
from .config import get_settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/api/plan", response_model=TravelResponse)
async def create_travel_plan(
    request: TravelRequest,
    settings=Depends(get_settings)
):
    try:
        logger.info(f"Processing travel plan request for destination: {request.destination}")
        
        graph = TravelPlannerGraph()
        state = graph.process_request({
            "destination": request.destination,
            "dates": request.dates,
            "preferences": request.preferences or ""
        })
        
        if not state.get("itinerary") or not state.get("plan"):
            logger.error("Failed to generate complete travel plan")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate complete travel plan. Please try again."
            )
        
        return TravelResponse(
            itinerary=state["itinerary"],
            plan=state["plan"],
            events=[event for event in state.get("content", []) if event]
        )
    except Exception as e:
        logger.error(f"Error processing travel plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process travel plan: {str(e)}"
        )