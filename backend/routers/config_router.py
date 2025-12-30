"""Handles API endpoints for managing application configuration."""

import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class APIKey(BaseModel):
    """Represents the structure for an API key submission."""
    apiKey: str

DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

@router.post("/api-key")
async def save_api_key(key: APIKey):
    """Saves the provided Groq API key to a local config file."""
    try:
        # Create the data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Save the API key to the config file
        config = {"groq_api_key": key.apiKey}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f)

        return {"message": "API Key saved successfully."}
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"File error: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}") from e
