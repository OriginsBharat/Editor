from fastapi import APIRouter, Body
from typing import Dict
from ..services import llm_service

router = APIRouter()

@router.post("/command")
async def process_command(payload: Dict[str, str] = Body(...)):
    """
    Accepts a natural language command and processes it.
    """
    command = payload.get("command")
    if not command:
        return {"error": "Command not provided"}

    response = llm_service.parse_command(command)
    return response
