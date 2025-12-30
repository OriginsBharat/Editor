from groq import Groq
import json
import os
from typing import Dict, Optional

def get_api_key() -> Optional[str]:
    """Reads the Groq API key from the config file."""
    config_path = os.path.join("data", "config.json")
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        config = json.load(f)
        return config.get("groq_api_key")

def parse_command(command: str) -> Dict[str, str]:
    """
    Parses a natural language command using the Groq API (Llama 3).
    """
    api_key = get_api_key()
    if not api_key:
        return {"error": "API key not found. Please save your API key in the configuration."}

    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant for a video editing suite. Your task is to parse user commands "
                        "and convert them into a structured JSON format. The JSON should have an 'action' key "
                        "(e.g., 'remove_text', 'add_subtitle', 'apply_filter') and other relevant parameters. "
                        "For a command like 'Remove the Chinese text from the video', the output should be "
                        "'{\"action\": \"remove_text\", \"language\": \"Chinese\"}'."
                    ),
                },
                {
                    "role": "user",
                    "content": command,
                },
            ],
            model="llama3-70b-8192",
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        return {"error": f"An error occurred with the Groq API: {str(e)}"}
