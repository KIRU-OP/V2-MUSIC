import aiohttp
from typing import Optional


JIOSAAVN_API = "https://jiosaavn-api.pashivam584.workers.dev/"


async def jiosaavn_search(query: str) -> Optional[dict]:
    """Search JioSaavn for a song. Returns first result dict or None."""
    url    = f"{JIOSAAVN_API}/api/search/songs"
    params = {"query": query, "page": 1, "limit": 1}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
        results = data.get("data", {}).get("results", [])
        return results[0] if results else None
    except Exception:
        return None


async def jiosaavn_song_details(song_id: str) -> Optional[dict]:
    """Fetch full song details by ID. Returns song dict or None."""
    url = f"{JIOSAAVN_API}/api/songs/{song_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
        results = data.get("data", [])
        return results[0] if results else None
    except Exception:
        return None


def jiosaavn_get_audio_url(song: dict) -> Optional[str]:
    """
    Extract best available audio URL from song dict.
    Priority: 320kbps → 160kbps → 96kbps → any available.
    """
    download_urls = song.get("downloadUrl", [])
    for quality in ["320kbps", "160kbps", "96kbps"]:
        for item in download_urls:
            if item.get("quality") == quality and item.get("url"):
                return item["url"]
    # Fallback: return any URL available
    for item in download_urls:
        if item.get("url"):
            return item["url"]
    return None


def jiosaavn_duration_to_seconds(song: dict) -> int:
    """Extract duration in seconds from song dict."""
    return int(song.get("duration", 0))
