import uuid
from dataclasses import dataclass, field
from typing import List

@dataclass
class DiscoveredArt:
    """Represents a piece of art found by the discovery service."""
    image_url: str
    artist: str
    source: str
    post_url: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

class ArtDiscoveryService:
    """
    Scrapes websites to find potential findom art.
    NOTE: This is a placeholder implementation.
    """
    def __init__(self):
        pass

    async def discover_art(self) -> List[DiscoveredArt]:
        """Finds new art from all configured sources."""
        print("🔍 Starting art discovery...")
        mock_art = self._get_mock_data()
        print(f"✨ Discovered {len(mock_art)} potential art pieces.")
        return mock_art

    def _get_mock_data(self) -> List[DiscoveredArt]:
        """Returns a list of mock art pieces for development and testing."""
        return [
            DiscoveredArt(
                image_url="https://i.pinimg.com/564x/4a/5b/f3/4a5bf336b3d1b8d27a10a1d6a6bcf3a1.jpg",
                artist="unknown_artist_1",
                source="Pinterest",
                post_url="https://www.pinterest.com/pin/12345/"
            ),
            DiscoveredArt(
                image_url="https://i.pinimg.com/564x/c7/2a/3a/c72a3a1f1a5c4e976f7a6a4d7d3b8f6f.jpg",
                artist="art_lover_99",
                source="Pinterest",
                post_url="https://www.pinterest.com/pin/23456/"
            ),
            DiscoveredArt(
                image_url="https://i.pinimg.com/564x/8d/6a/c7/8d6ac7b4f3a743a62d04f261a9c7b9a5.jpg",
                artist="creative_mind",
                source="Pinterest",
                post_url="https://www.pinterest.com/pin/34567/"
            ),
            DiscoveredArt(
                image_url="https://i.pinimg.com/564x/f8/c4/f4/f8c4f4b1e563381a5a5b5c9d1c8a1b2d.jpg",
                artist="photographer_x",
                source="Pinterest",
                post_url="https://www.pinterest.com/pin/45678/"
            ),
            DiscoveredArt(
                image_url="https://i.pinimg.com/564x/a1/b1/c1/a1b1c1b1b1b1b1b1b1b1b1b1b1b1b1b1.jpg",
                artist="goddess_art",
                source="Pinterest",
                post_url="https://www.pinterest.com/pin/56789/"
            ),
        ]
