from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import List
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)

PLAN_PROMPT = """You are an expert travel planner tasked with creating a high-level 
itinerary outline. Write such an outline for the user provided destination and dates. 
Consider any user preferences provided. Give a concise but informative outline of the itinerary."""

RESEARCH_PROMPT = """You are a travel planner tasked with finding events for a user visiting. 
Generate a list of search queries that will gather information on local events during this 
period such as music festivals, food fairs, technical conferences, or any other noteworthy 
events. Consider the user's preferences in generating these queries. Generate exactly 3 queries."""

ITINERARY_PROMPT = """You are a travel agent tasked with creating the best possible 
travel itinerary for the user's trip. Generate a detailed day-by-day itinerary based on 
the provided destination, dates, and research information. Include specific times, 
locations, and activities. Consider the user's preferences in the planning.

Previous plan:
{plan}

Research information:
{research}

User preferences:
{preferences}
"""

class LLMService:
    def __init__(self):
        logger.info("Initializing LLM service...")
        try:
            settings = get_settings()
            self.llm = ChatGroq(
                    api_key=settings.LLM_API_KEY,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
            )
            logger.info("LLM service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise
    
    def generate_plan(self, destination: str, dates: str, preferences: str) -> str:
        logger.info(f"Generating plan for {destination}")
        try:
            messages = [
                SystemMessage(content=PLAN_PROMPT),
                HumanMessage(content=f"Destination: {destination}\n\nDates: {dates}\n\nPreferences: {preferences}")
            ]
            response = self.llm.invoke(messages)
            logger.info("Plan generated successfully")
            return response.content
        except Exception as e:
            logger.error(f"Error generating plan: {str(e)}")
            raise
    
    def generate_search_queries(self, destination: str, dates: str, preferences: str) -> List[str]:
        logger.info(f"Generating search queries for {destination}")
        try:
            messages = [
                SystemMessage(content=RESEARCH_PROMPT),
                HumanMessage(content=f"Destination: {destination}\n\nDates: {dates}\n\nPreferences: {preferences}")
            ]
            response = self.llm.invoke(messages)
            queries = [q.strip() for q in response.content.split('\n') if q.strip()]
            logger.info(f"Generated {len(queries)} search queries")
            return queries[:3]
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            raise
    
    def generate_itinerary(self, destination: str, dates: str, plan: str, 
                          research: List[str], preferences: str) -> str:
        logger.info(f"Generating itinerary for {destination}")
        try:
            research_text = "\n\n".join(research)
            messages = [
                SystemMessage(content=ITINERARY_PROMPT.format(
                    plan=plan,
                    research=research_text,
                    preferences=preferences
                )),
                HumanMessage(content=f"Destination: {destination}\n\nDates: {dates}")
            ]
            response = self.llm.invoke(messages)
            logger.info("Itinerary generated successfully")
            return response.content
        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            raise