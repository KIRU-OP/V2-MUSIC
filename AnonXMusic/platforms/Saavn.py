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
        # API Endpoint check
        url = f"{self.api_url}/api/search/songs"
        params = {"query": str(query)}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
            
            # Debugging: Agar aap terminal check karenge to wahan data dikhega
            if not data or data.get("status") != "SUCCESS":
                return None

            # Pashivam API structure: data -> data -> results
            # Kabhi-kabhi data['data'] hi results ki list hoti hai
            res_data = data.get("data")
            if isinstance(res_data, dict):
                results = res_data.get("results", [])
            elif isinstance(res_data, list):
                results = res_data
            else:
                results = []

            if results:
                return results[0]
            return None
        except Exception as e:
            print(f"Search Exception: {e}")
            return None

    async def get_link(self, query: str):
        data = await self.search(query)
        if not data:
            return None
        
        try:
            # Name and Title handle
            title = data.get("name") or data.get("title") or "Unknown Song"
            duration = int(data.get("duration", 0))
            
            # Thumbnail
            images = data.get("image")
            thumbnail = None
            if isinstance(images, list) and images:
                thumbnail = images[-1].get("url")
            elif isinstance(images, str):
                thumbnail = images

            # Audio Link (Download URL)
            download_urls = data.get("downloadUrl")
            stream_url = None
            
            if isinstance(download_urls, list) and download_urls:
                # Sabse pehle 320kbps dhoondho
                for item in download_urls:
                    if item.get("quality") == "320kbps":
                        stream_url = item.get("url")
                        break
                # Agar nahi mila to pehla wala le lo
                if not stream_url:
                    stream_url = download_urls[-1].get("url")
            
            if not stream_url:
                return None

            return title, duration, thumbnail, stream_url
        except Exception as e:
            print(f"Parsing Exception: {e}")
            return None
