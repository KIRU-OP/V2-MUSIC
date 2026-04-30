# Powered by: Kiru_Op
# YouTube Anti-Ban + Enhanced Metadata Fetching

import asyncio
import os
import re
import random
import time
import aiohttp
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

# Library handling for YouTube Search
try:
    from youtubesearchpython.__future__ import VideosSearch, Playlist
except ImportError:
    try:
        from youtubesearchpython import VideosSearch, Playlist
    except ImportError:
        from ytSearch import VideosSearch, Playlist

# Folder and Cookie Setup
SESSION_DIR = "./bot_session"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

COOKIE_FILE = os.path.join(SESSION_DIR, "cookies.txt")
SAAVN_API_URL = "https://jiosaavn-api.pashivam584.workers.dev"

if not os.path.exists(COOKIE_FILE):
    with open(COOKIE_FILE, "w") as f:
        f.write("")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    def get_ytdl_opts(self, is_video=False):
        opts = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "headers": {
                "User-Agent": self.user_agent,
                "Accept-Language": "en-US,en;q=0.9",
            },
            "extractor_args": {
                "youtube": {
                    "player_client": ["web_creator", "tv", "mweb"],
                    "player_skip": ["webpage", "configs"],
                }
            },
            "format": "best[height<=720]/best" if is_video else "bestaudio/best",
            "source_address": "0.0.0.0",
            "retries": 3,
        }
        if os.path.exists(COOKIE_FILE) and os.path.getsize(COOKIE_FILE) > 10:
            opts["cookiefile"] = COOKIE_FILE
        return opts

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Method 1: Using youtubesearchpython (Fast)
        try:
            search = VideosSearch(link, limit=1)
            import inspect
            if inspect.iscoroutinefunction(search.next):
                result = (await search.next())["result"]
            else:
                result = search.result()["result"]
            
            if result:
                res = result[0]
                return (
                    res.get("title", "Unknown"),
                    res.get("duration", "00:00"),
                    0, # Placeholder for seconds
                    res["thumbnails"][0]["url"].split("?")[0],
                    res.get("id", "None")
                )
        except Exception:
            pass # Fallback to Method 2

        # Method 2: Using yt-dlp (Robust - works when search fails)
        try:
            opts = self.get_ytdl_opts()
            loop = asyncio.get_running_loop()
            def _extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(link, download=False)
            
            info = await loop.run_in_executor(None, _extract)
            return (
                info.get("title", "Unknown"),
                "00:00", # Duration logic can be added if needed
                info.get("duration", 0),
                info.get("thumbnail", "https://telegra.ph/file/default.jpg"),
                info.get("id", "None")
            )
        except Exception as e:
            print(f"Details Error: {e}")
            return "Unknown", "00:00", 0, "https://telegra.ph/file/default.jpg", "None"

    async def track(self, link: str, videoid: Union[bool, str] = None):
        """Fetches track details and ensures it doesn't return None"""
        title, duration, seconds, thumb, vidid = await self.details(link, videoid)
        if vidid == "None" and not videoid:
             # Agar link search fail ho jaye, toh ID nikalne ki koshish karein
             vidid = link.split("v=")[-1] if "v=" in link else link.split("/")[-1]

        track_details = {
            "title": title,
            "link": self.base + vidid,
            "vidid": vidid,
            "duration_min": duration,
            "thumb": thumb,
        }
        return track_details, vidid

    # --- Saavn Support ---
    async def saavn_search(self, query: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{SAAVN_API_URL}/search/songs", params={"query": query}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("data", {}).get("results", [])
            return []
        except: return []

    async def saavn_details(self, song_id: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{SAAVN_API_URL}/songs", params={"id": song_id}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        song = data.get("data", [{}])[0]
                        return {
                            "title": song.get("name"),
                            "url": song.get("downloadUrl", [])[-1].get("link"),
                            "thumb": song.get("image", [{}])[-1].get("link"),
                            "duration": song.get("duration")
                        }
            return None
        except: return None

    # --- Video & Download ---
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        opts = self.get_ytdl_opts(is_video=True)
        try:
            loop = asyncio.get_running_loop()
            def extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(link, download=False).get('url')
            url = await loop.run_in_executor(None, extract)
            return (1, url) if url else (0, "No URL found")
        except Exception as e: return 0, str(e)

    async def download(self, link: str, video: bool = False, **kwargs):
        loop = asyncio.get_running_loop()
        try:
            def _get_stream():
                with yt_dlp.YoutubeDL(self.get_ytdl_opts(is_video=video)) as ydl:
                    return ydl.extract_info(link, download=False)['url']
            return await loop.run_in_executor(None, _get_stream), None
        except Exception as e: return str(e), False
