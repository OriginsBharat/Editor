"""Main FastAPI application for Project Pratyaharthi."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import video_router, command_router, config_router

app = FastAPI()

# Serve the frontend's static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    """Serves the main index.html file."""
    return FileResponse('frontend/index.html')

# Include the API routers
app.include_router(video_router.router, prefix="/video", tags=["video"])
app.include_router(command_router.router, prefix="/control", tags=["control"])
app.include_router(config_router.router, prefix="/config", tags=["config"])
