from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os

router = APIRouter()

class APIKey(BaseModel):
    apiKey: str

DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

@router.post("/api-key")
async def save_api_key(key: APIKey):
    try:
        # Create the data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Save the API key to the config file
        config = {"groq_api_key": key.apiKey}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

        return {"message": "API Key saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
