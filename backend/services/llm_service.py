from typing import Dict

def parse_command(command: str) -> Dict[str, str]:
    """
    Placeholder function to parse a natural language command.
    In the future, this will interact with the Groq API.
    """
    print(f"Received command: {command}")
    # Mock response for now
    command_lower = command.lower()
    if "remove" in command_lower and "text" in command_lower:
        return {"action": "remove_text", "target": "latest_video.mp4"}
    else:
        return {"action": "unknown", "details": "Command not understood"}
