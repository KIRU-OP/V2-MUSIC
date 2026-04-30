import re
import aiohttp
from typing import Optional

class SaavnAPI:
    def __init__(self):
        self.api_url = "https://jiosaavn-api.pashivam584.workers.dev"

    async def search(self, query: str):
        # Query clean karein
        query = query.lower().replace("play", "").strip()
        url = f"{self.api_url}/api/search/songs"
        params = {"query": query}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
            
            results = []
            if "data" in data:
                if isinstance(data["data"], dict):
                    results = data["data"].get("results", [])
                elif isinstance(data["data"], list):
                    results = data["data"]
            elif "results" in data:
                results = data["results"]

            return results[0] if results else None
        except Exception:
            return None

    async def get_link(self, query: str):
        data = await self.search(query)
        if not data:
            return None
        try:
            title = data.get("name") or data.get("title") or "JioSaavn Song"
            duration = int(data.get("duration", 0))
            images = data.get("image", [])
            thumbnail = images[-1].get("url") if isinstance(images, list) and images else images
            
            download_urls = data.get("downloadUrl", [])
            stream_url = None
            if isinstance(download_urls, list) and download_urls:
                for item in download_urls:
                    if item.get("quality") == "320kbps":
                        stream_url = item.get("url")
                        break
                if not stream_url:
                    stream_url = download_urls[-1].get("url")
            
            return title, duration, thumbnail, stream_url
        except Exception:
            return None
