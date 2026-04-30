import re
import aiohttp
from typing import Optional

class SaavnAPI:
    def __init__(self):
        self.api_url = "https://jiosaavn-api.pashivam584.workers.dev"
        self.regex = r"^(https?:\/\/)?(www\.)?(jiosaavn\.com\/song\/.*)$"

    async def search(self, query: str):
        # Pashivam API endpoint fix
        url = f"{self.api_url}/api/search/songs"
        params = {"query": str(query)}
        
        print(f"DEBUG: Saavn searching for: {query}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    print(f"DEBUG: Saavn API Status: {resp.status}")
                    if resp.status != 200:
                        return None
                    data = await resp.json()
            
            if data.get("status") != "SUCCESS":
                print(f"DEBUG: Saavn API returned status: {data.get('status')}")
                return None

            # Pashivam API structure handle
            res_data = data.get("data")
            if isinstance(res_data, dict):
                results = res_data.get("results", [])
            elif isinstance(res_data, list):
                results = res_data
            else:
                results = []

            if results:
                print(f"DEBUG: Found song: {results[0].get('name')}")
                return results[0]
            
            print("DEBUG: No results found in API response.")
            return None
        except Exception as e:
            print(f"DEBUG: Saavn API Exception: {e}")
            return None

    async def get_link(self, query: str):
        data = await self.search(query)
        if not data:
            return None
        
        try:
            title = data.get("name") or data.get("title")
            duration = int(data.get("duration", 0))
            
            # Thumbnail logic
            images = data.get("image")
            thumbnail = images[-1].get("url") if isinstance(images, list) else images
            
            # Audio Link (320kbps is best)
            download_urls = data.get("downloadUrl")
            stream_url = None
            if isinstance(download_urls, list):
                for item in download_urls:
                    if item.get("quality") == "320kbps":
                        stream_url = item.get("url")
                        break
                if not stream_url:
                    stream_url = download_urls[-1].get("url")
            
            if not stream_url:
                print("DEBUG: Stream URL not found in data.")
                return None

            return title, duration, thumbnail, stream_url
        except Exception as e:
            print(f"DEBUG: Parsing Error: {e}")
            return None
