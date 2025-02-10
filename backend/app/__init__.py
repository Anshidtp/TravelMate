from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(title="Travel Planner API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app