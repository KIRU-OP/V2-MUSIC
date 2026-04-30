import re
import aiohttp
from typing import Optional

class SaavnAPI:
    def __init__(self):
        self.api_url = "https://jiosaavn-api.pashivam584.workers.dev"
        self.regex = r"^(https?:\/\/)?(www\.)?(jiosaavn\.com\/song\/.*)$"

    async def valid(self, link: str):
        if re.match(self.regex, link):
            return True
        return False

    async def search(self, query: str):
        url = f"{self.api_url}/api/search/songs"
        params = {"query": query, "page": 1, "limit": 1}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    data = await resp.json()
            if data.get("status") == "SUCCESS":
                results = data.get("data", {}).get("results", [])
                return results[0] if results else None
            return None
        except Exception:
            return None

    async def get_link(self, query: str):
        data = await self.search(query)
        if not data:
            return None
        
        title = data.get("name")
        duration = int(data.get("duration", 0))
        thumbnail = data.get("image", [{}])[-1].get("url")
        
        download_urls = data.get("downloadUrl", [])
        stream_url = None
        for q in ["320kbps", "160kbps", "96kbps"]:
            for item in download_urls:
                if item.get("quality") == q:
                    stream_url = item.get("url")
                    break
            if stream_url: break
        
        if not stream_url and download_urls:
            stream_url = download_urls[0].get("url")
            
        return title, duration, thumbnail, stream_url
