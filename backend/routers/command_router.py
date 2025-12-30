"""Handles API endpoints for processing user commands."""

from typing import Dict
from fastapi import APIRouter, Body, HTTPException
from backend.services import llm_service

router = APIRouter()

@router.post("/command")
async def process_command(payload: Dict[str, str] = Body(...)):
    """
    Accepts a natural language command and processes it using the LLM service.
    """
    command = payload.get("command")
    if not command:
        raise HTTPException(status_code=422, detail="Command not provided")

    response = llm_service.parse_command(command)
    return response
