from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from findom_manager.services.ai import AIService
from findom_manager.services.art_discovery import DiscoveredArt

@dataclass
class VettedArt(DiscoveredArt):
    """Represents a piece of art that has been analyzed by the AI."""
    ai_analysis: Dict[str, Any]
    is_approved_for_review: bool
    rejection_reason: Optional[str] = None

class ArtVettingService:
    """
    Uses AI to analyze and vet discovered art pieces.
    """
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def vet_art_pieces(self, art_pieces: List[DiscoveredArt]) -> List[VettedArt]:
        """
        Takes a list of discovered art and returns a list of vetted art.
        """
        print(f"🤖 Starting AI vetting for {len(art_pieces)} pieces...")
        vetted_art_list = []
        for art in art_pieces:
            analysis = await self.ai_service.analyze_image(art.image_url)
            vetted_art = self._evaluate_art(art, analysis)
            vetted_art_list.append(vetted_art)

            status = "✅ PASSED" if vetted_art.is_approved_for_review else f"❌ REJECTED ({vetted_art.rejection_reason})"
            print(f"  - Vetting {art.post_url}: {status}")

        print("✨ Vetting complete.")
        return vetted_art_list

    def _evaluate_art(self, art: DiscoveredArt, analysis: Optional[Dict[str, Any]]) -> VettedArt:
        """
        Evaluates a single piece of art based on the AI's analysis.
        """
        if not analysis:
            return VettedArt(
                **art.__dict__,
                ai_analysis={"error": "AI analysis failed"},
                is_approved_for_review=False,
                rejection_reason="AI analysis failed"
            )

        # --- Hard Rejection Criteria ---
        if not analysis.get("is_male_dom"):
            return VettedArt(**art.__dict__, ai_analysis=analysis, is_approved_for_review=False, rejection_reason="Not male dom")

        if not analysis.get("is_findom_theme"):
            return VettedArt(**art.__dict__, ai_analysis=analysis, is_approved_for_review=False, rejection_reason="Not findom theme")

        if not analysis.get("is_illustration"):
            return VettedArt(**art.__dict__, ai_analysis=analysis, is_approved_for_review=False, rejection_reason="Is a real photo")

        # --- Soft Rejection Criteria (based on scores) ---
        if analysis.get("quality_score", 0) < 5:
             return VettedArt(**art.__dict__, ai_analysis=analysis, is_approved_for_review=False, rejection_reason=f"Low quality (score: {analysis.get('quality_score')})")

        if analysis.get("confidence", 0) < 60:
             return VettedArt(**art.__dict__, ai_analysis=analysis, is_approved_for_review=False, rejection_reason=f"Low confidence (score: {analysis.get('confidence')})")

        # If all checks pass, it's approved for the Master's review
        return VettedArt(**art.__dict__, ai_analysis=analysis, is_approved_for_review=True)
