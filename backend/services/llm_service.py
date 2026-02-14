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
            "The JSON must have an 'action' key and any relevant parameters. "
            "Valid actions are 'remove_text' and 'translate_video'. "
            "For 'remove_text', also include the 'language'. "
            "For 'translate_video', also include the 'character'.\n\n"
            "Example 1:\nUser command: 'Remove the Chinese text from the video.'\n"
            "JSON output: {\"action\": \"remove_text\", \"language\": \"Chinese\"}\n\n"
            "Example 2:\nUser command: 'Translate the video in the style of Gojo Satoru.'\n"
            "JSON output: {\"action\": \"translate_video\", \"character\": \"Gojo Satoru\"}"
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

def translate_and_style_text(text_to_translate: str, voice_profile: Dict) -> str:
    """
    Translates text into English, stylized according to the character's voice profile.
    """
    try:
        client = Groq()

        system_prompt = (
            "You are an expert translator specializing in creative, in-character dialogue for anime. "
            "Your task is to translate the given text into English. Crucially, you must adopt the "
            "exact personality and speech patterns described in the provided voice profile. "
            "Do NOT break character. Only return the translated text. Do not add any commentary."
        )

        user_prompt = (
            f"**Voice Profile:**\nName: {voice_profile['name']}\n"
            f"Description: {voice_profile['description']}\n\n"
            f"**Text to Translate:**\n\"{text_to_translate}\""
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7, # Higher temperature for more creative, stylized output
            max_tokens=1024,
        )

        return chat_completion.choices[0].message.content.strip()

    except GroqError as e:
        return f"Error: API error during translation: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred during translation: {str(e)}"
