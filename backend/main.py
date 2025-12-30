from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import video_router, command_router, config_router
import os

app = FastAPI()

# Serve the frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')


app.include_router(video_router.router, prefix="/video", tags=["video"])
app.include_router(command_router.router, prefix="/control", tags=["control"])
app.include_router(config_router.router, prefix="/config", tags=["config"])
