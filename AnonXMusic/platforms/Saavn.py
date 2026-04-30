import re
import aiohttp
from typing import Optional

class SaavnAPI:
    def __init__(self):
        # Aapki working API
        self.api_url = "https://jiosaavn-api.pashivam584.workers.dev"
        self.regex = r"^(https?:\/\/)?(www\.)?(jiosaavn\.com\/song\/.*)$"

    async def valid(self, link: str):
        if re.match(self.regex, link):
            return True
        return False

    async def search(self, query: str):
        # Pashivam API usually uses /api/search/songs
        url = f"{self.api_url}/api/search/songs"
        params = {"query": query}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
            
            # Pashivam API structure: data -> results -> [0]
            if data.get("status") == "SUCCESS":
                inner_data = data.get("data", {})
                if isinstance(inner_data, dict):
                    results = inner_data.get("results", [])
                else:
                    results = inner_data # Kuch versions mein direct list hoti hai
                
                if results and len(results) > 0:
                    return results[0]
            return None
        except Exception as e:
            print(f"Saavn Search Error: {e}")
            return None

    async def get_link(self, query: str):
        data = await self.search(query)
        if not data:
            return None
        
        try:
            # Metadata extraction
            title = data.get("name", "Unknown Song")
            duration = int(data.get("duration", 0))
            
            # Thumbnail extraction (Last one is highest quality)
            images = data.get("image", [])
            thumbnail = images[-1].get("url") if images else None
            
            # Audio link extraction (320kbps is best)
            download_urls = data.get("downloadUrl", [])
            stream_url = None
            
            if download_urls:
                # 320kbps check karein
                for item in download_urls:
                    if item.get("quality") == "320kbps":
                        stream_url = item.get("url")
                        break
                # Agar 320 nahi mila to koi bhi (usually last one is better)
                if not stream_url:
                    stream_url = download_urls[-1].get("url")
            
            return title, duration, thumbnail, stream_url
        except Exception as e:
            print(f"Saavn Parsing Error: {e}")
            return None
