import re
import aiohttp
from typing import Optional

class SaavnAPI:
    def __init__(self):
        self.api_url = "https://jiosaavn-api.pashivam584.workers.dev"

    async def search(self, query: str):
        # Query se 'play' shabd hatayein aur clean karein
        clean_query = query.lower().replace("play", "").strip()
        url = f"{self.api_url}/api/search/songs"
        params = {"query": clean_query}
        
        print(f"DEBUG: Searching JioSaavn for: {clean_query}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as resp:
                    print(f"DEBUG: API Status Code: {resp.status}")
                    if resp.status != 200:
                        return None
                    data = await resp.json()

            # DEBUG: Terminal mein JSON keys dekhein
            print(f"DEBUG: API Keys received: {list(data.keys())}")

            # Flexible Parsing (Check all possible locations for results)
            results = []
            
            # Location 1: data -> results (Common)
            if "results" in data:
                results = data["results"]
            # Location 2: data -> data -> results (Pashivam style)
            elif "data" in data:
                if isinstance(data["data"], dict):
                    results = data["data"].get("results", [])
                elif isinstance(data["data"], list):
                    results = data["data"]
            
            # Agar results mil gaye hain
            if results and len(results) > 0:
                song = results[0]
                print(f"DEBUG: Success! Song Found: {song.get('name')}")
                return song
            
            print("DEBUG: No results found in the JSON structure.")
            return None

        except Exception as e:
            print(f"DEBUG: Saavn API Exception: {e}")
            return None

    async def get_link(self, query: str):
        data = await self.search(query)
        if not data:
            return None
        try:
            # Metadata handle karein (name ya title)
            title = data.get("name") or data.get("title") or "Unknown"
            duration = int(data.get("duration", 0))
            
            # Images list mein se best quality
            images = data.get("image", [])
            thumbnail = images[-1].get("url") if isinstance(images, list) and images else images
            
            # Audio links list mein se 320kbps
            download_urls = data.get("downloadUrl", [])
            stream_url = None
            if isinstance(download_urls, list) and download_urls:
                for item in download_urls:
                    if item.get("quality") == "320kbps":
                        stream_url = item.get("url")
                        break
                if not stream_url:
                    stream_url = download_urls[-1].get("url")
            
            if not stream_url:
                print("DEBUG: Stream URL missing in song data.")
                return None

            return title, duration, thumbnail, stream_url
        except Exception as e:
            print(f"DEBUG: Parsing Error: {e}")
            return None
