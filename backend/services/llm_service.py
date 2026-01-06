"""Handles interaction with the Groq Large Language Model API."""

import json
import os
from typing import Dict
from groq import Groq, GroqError

def parse_command(command: str) -> Dict[str, str]:
    """
    Parses a natural language command using the Groq API (Llama 3).
    The API key is automatically read from the GROQ_API_KEY environment variable.
    """
    try:
        # The Groq client automatically reads the GROQ_API_KEY from the environment.
        # If it's not set, the constructor will raise an error.
        client = Groq()
        system_prompt = (
            "You are an AI assistant for a video editing suite. Your task is to "
            "parse user commands and convert them into a structured JSON format. "
            "The JSON should have an 'action' key (e.g., 'remove_text', "
            "'add_subtitle', 'apply_filter') and other relevant parameters. "
            "For 'Remove Chinese text', output '{\"action\": \"remove_text\", "
            "\"language\": \"Chinese\"}'."
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)

    except GroqError as e:
        # Check if the error is due to a missing API key.
        if "api key" in str(e).lower():
            return {"error": "GROQ_API_KEY environment variable not set. Please set it before running the application."}
        return {"error": f"An API error occurred: {e}"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode the API response."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
