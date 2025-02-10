from langgraph.graph import StateGraph, START, END
from tavily import TavilyClient
from typing import Dict, Any
import logging

from ..config import get_settings
from ..models import State
from .llm_service import LLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelPlannerGraph:
    def __init__(self):
        settings = get_settings()
        self.llm_service = LLMService()
        self.tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        logger.info("Building graph...")
        graph_builder = StateGraph(State)
        
        # Add nodes with unique keys for state updates
        graph_builder.add_node("create_plan", self._plan_node)
        graph_builder.add_node("do_research", self._research_node)
        graph_builder.add_node("generate_itinerary", self._generation_node)
        
        # Add edges with proper flow
        graph_builder.add_edge(START, "create_plan")
        graph_builder.add_edge("create_plan", "do_research")
        graph_builder.add_edge("do_research", "generate_itinerary")
        graph_builder.add_edge("generate_itinerary", END)
        
        logger.info("Graph built successfully")
        return graph_builder.compile()
    
    def _plan_node(self, state: State) -> Dict[str, Any]:
        logger.info("Executing plan node...")
        try:
            logger.info(f"Generating plan for destination: {state['destination']}")
            initial_plan = self.llm_service.generate_plan(
                state["destination"], 
                state["dates"],
                state.get("preferences", "")
            )
            logger.info("Plan generated successfully")
            return {"plan": initial_plan}
        except Exception as e:
            logger.error(f"Error in plan node: {str(e)}")
            raise Exception(f"Plan node failed: {str(e)}")
    
    def _research_node(self, state: State) -> Dict[str, Any]:
        logger.info("Executing research node...")
        try:
            queries = self.llm_service.generate_search_queries(
                state["destination"],
                state["dates"],
                state.get("preferences", "")
            )
            logger.info(f"Generated {len(queries)} search queries")
            
            content = []
            for i, query in enumerate(queries):
                try:
                    logger.info(f"Executing search query {i + 1}: {query}")
                    results = self.tavily.search(query=query, max_results=2)
                    content.extend(r["content"] for r in results["results"])
                except Exception as e:
                    logger.error(f"Error in Tavily search for query '{query}': {str(e)}")
                    continue
            
            logger.info(f"Research completed with {len(content)} results")
            return {"content": content}
        except Exception as e:
            logger.error(f"Error in research node: {str(e)}")
            raise Exception(f"Research node failed: {str(e)}")
    
    def _generation_node(self, state: State) -> Dict[str, Any]:
        logger.info("Executing generation node...")
        try:
            logger.info("Generating final itinerary")
            final_itinerary = self.llm_service.generate_itinerary(
                state["destination"],
                state["dates"],
                state["plan"],
                state["content"],
                state.get("preferences", "")
            )
            logger.info("Itinerary generated successfully")
            return {"itinerary": final_itinerary}
        except Exception as e:
            logger.error(f"Error in generation node: {str(e)}")
            raise Exception(f"Generation node failed: {str(e)}")
    
    def process_request(self, request_data: dict) -> Dict[str, Any]:
        logger.info("Processing request...")
        # Initialize state with request data
        initial_state = {
            "destination": request_data["destination"],
            "dates": request_data["dates"],
            "preferences": request_data.get("preferences", ""),
            "plan": "",
            "content": [],
            "itinerary": ""
        }
        
        thread = {"configurable": {"thread_id": "1"}}
        final_state = None
        
        try:
            logger.info("Starting graph execution")
            for state in self.graph.stream(initial_state, thread):
                logger.info(f"Current state keys: {state.keys()}")
                final_state = state
            
            if not final_state:
                raise Exception("Graph execution completed but no final state was produced")
                
            logger.info("Request processed successfully")
            return final_state
        except Exception as e:
            logger.error(f"Error in graph processing: {str(e)}")
            raise Exception(f"Graph processing failed: {str(e)}")