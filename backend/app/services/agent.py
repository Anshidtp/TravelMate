from langgraph.graph import StateGraph, START, END
from tavily import TavilyClient
from typing import Dict, Any
from ..config import get_settings
from ..models import State
from .llm_service import LLMService

class TravelPlannerGraph:
    def __init__(self):
        settings = get_settings()
        self.llm_service = LLMService()
        self.tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        
        # Add nodes
        graph_builder.add_node("plan", self._plan_node)
        graph_builder.add_node("research", self._research_node)
        graph_builder.add_node("generate", self._generation_node)
        
        # Add edges
        graph_builder.add_edge(START, "plan")
        graph_builder.add_edge("plan", "research")
        graph_builder.add_edge("research", "generate")
        graph_builder.add_edge("generate", END)
        
        return graph_builder.compile()
    
    def _plan_node(self, state: State) -> Dict[str, Any]:
        plan = self.llm_service.generate_plan(
            state["destination"], 
            state["dates"],
            state.get("preferences", "")
        )
        return {"plan": plan}
    
    def _research_node(self, state: State) -> Dict[str, Any]:
        queries = self.llm_service.generate_search_queries(
            state["destination"],
            state["dates"],
            state.get("preferences", "")
        )
        
        content = []
        for query in queries:
            try:
                results = self.tavily.search(query=query, max_results=2)
                content.extend(r["content"] for r in results["results"])
            except Exception as e:
                print(f"Error in Tavily search for query '{query}': {str(e)}")
                continue
                
        return {"content": content}
    
    def _generation_node(self, state: State) -> Dict[str, Any]:
        itinerary = self.llm_service.generate_itinerary(
            state["destination"],
            state["dates"],
            state["plan"],
            state["content"],
            state.get("preferences", "")
        )
        return {"itinerary": itinerary}
    
    def process_request(self, request_data: dict) -> Dict[str, Any]:
        thread = {"configurable": {"thread_id": "1"}}
        final_state = None
        
        for state in self.graph.stream(request_data, thread):
            final_state = state
            
        return final_state