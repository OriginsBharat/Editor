from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import video_router, command_router

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(video_router.router, prefix="/video", tags=["video"])
app.include_router(command_router.router, prefix="/control", tags=["control"])

@app.get("/")
async def root():
    return {"message": "Welcome to Project Pratyaharthi"}
