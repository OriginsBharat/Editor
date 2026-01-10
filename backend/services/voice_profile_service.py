"""
This service manages character voice profiles for stylized text translation.
"""
import logging
from typing import Dict, Optional

# --- Logging Setup ---
log = logging.getLogger(__name__)

# --- Hardcoded Voice Profile Database ---
# This will be expanded later with the Auto-Discovery Protocol.
_VOICE_PROFILES: Dict[str, Dict[str, str]] = {
    "gojo satoru": {
        "name": "Gojo Satoru",
        "description": (
            "Speaks with a mix of arrogance, playfulness, and confidence. "
            "Uses casual language, slang (like 'lol' or 'y'know'), and often teases others. "
            "He can be serious when necessary, but his default tone is laid-back and self-assured."
        )
    },
    "pain": {
        "name": "Pain (Nagato)",
        "description": (
            "Speaks in a formal, detached, and philosophical tone. Uses biblical or god-like language. "
            "His dialogue is often about suffering, justice, and the cycle of hatred. "
            "He is calm, deliberate, and never uses casual language or contractions."
        )
    },
    "vegeta": {
        "name": "Vegeta",
        "description": (
            "Speaks with extreme arrogance, pride, and aggression. "
            "Frequently underestimates his opponents and boasts about his Saiyan heritage. "
            "He is confrontational, impatient, and uses sharp, direct language. Often refers to others with contempt."
        )
    }
}

def get_voice_profile(character_name: str) -> Optional[Dict[str, str]]:
    """
    Retrieves a character's voice profile from the database.
    The search is case-insensitive.
    """
    log.info("Searching for voice profile for: %s", character_name)
    profile = _VOICE_PROFILES.get(character_name.lower())
    if profile:
        log.info("Found profile for %s.", character_name)
        return profile

    log.warning("No voice profile found for: %s", character_name)
    # In the future, this is where the Auto-Discovery Protocol will be triggered.
    return None
