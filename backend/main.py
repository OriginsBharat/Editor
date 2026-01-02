"""Main FastAPI application for Project Pratyaharthi."""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

log.info("Starting FastAPI application...")
log.info("Importing routers...")
from backend.routers import command_router, config_router
log.info("Routers imported successfully.")

app = FastAPI(
    title="Project Pratyaharthi",
    description="An AI-driven automated video localization suite.",
    version="1.7.12",
)

# Serve the frontend's static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    """Serves the main index.html file."""
    return FileResponse('frontend/index.html')

# Include the API routers
log.info("Including routers...")
app.include_router(command_router.router, prefix="/api/commands", tags=["command"])
app.include_router(config_router.router, prefix="/api/config", tags=["config"])
log.info("Routers included successfully.")

if __name__ == "__main__":
    log.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
