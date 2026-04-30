import aiohttp
from typing import Optional

class SaavnAPI:
    def __init__(self):
        self.api_url = "https://jiosaavn-api.pashivam584.workers.dev"

    async def search(self, query: str) -> Optional[dict]:
        """Search JioSaavn for a song."""
        url = f"{self.api_url}/api/search/songs"
        params = {"query": query, "page": 1, "limit": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
            results = data.get("data", {}).get("results", [])
            return results[0] if results else None
        except Exception:
            return None

    async def song_details(self, song_id: str) -> Optional[dict]:
        """Fetch full song details by ID."""
        url = f"{self.api_url}/api/songs/{song_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
            results = data.get("data", [])
            return results[0] if results else None
        except Exception:
            return None

    def get_audio_url(self, song: dict) -> Optional[str]:
        """Extract best available audio URL."""
        download_urls = song.get("downloadUrl", [])
        if not download_urls:
            return None
        # Priority: 320kbps → 160kbps → 96kbps
        for quality in ["320kbps", "160kbps", "96kbps"]:
            for item in download_urls:
                if item.get("quality") == quality and item.get("url"):
                    return item["url"]
        return download_urls[0].get("url")

    def duration_to_seconds(self, song: dict) -> int:
        return int(song.get("duration", 0))
