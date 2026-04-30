# Powered by: Kiru_Op
# YouTube Anti-Ban + JioSaavn Cloudflare Bypass Integration

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

# Ensure cookie file exists
if not os.path.exists(COOKIE_FILE):
    with open(COOKIE_FILE, "w") as f:
        f.write("")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        
        # Consistent User-Agent for Cookie Sync
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    # --- JIOSAAVN API INTEGRATION ---

    async def saavn_search(self, query: str):
        """Search songs on JioSaavn for high-quality audio fallback"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{SAAVN_API_URL}/search/songs", params={"query": query}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("data", {}).get("results", [])
            return []
        except:
            return []

    async def saavn_details(self, song_id: str):
        """Get direct 320kbps link from Saavn"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{SAAVN_API_URL}/songs", params={"id": song_id}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        song = data.get("data", [{}])[0]
                        dl_urls = song.get("downloadUrl", [])
                        return {
                            "title": song.get("name"),
                            "url": dl_urls[-1].get("link") if dl_urls else None,
                            "thumb": song.get("image", [{}])[-1].get("link"),
                            "duration": song.get("duration")
                        }
            return None
        except:
            return None

    # --- YOUTUBE OPTIMIZED METHODS ---

    def get_ytdl_opts(self, is_video=False):
        """Strongest extraction settings to avoid 'Sign in to confirm'"""
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
                    # 'web_creator' is currently the most stable client for bypassing login
                    "player_client": ["web_creator", "tv", "mweb"],
                    "player_skip": ["webpage", "configs"],
                }
            },
            "format": "best[height<=720]/best" if is_video else "bestaudio/best",
            "source_address": "0.0.0.0", # Force IPv4
            "retries": 3,
        }
        if os.path.exists(COOKIE_FILE) and os.path.getsize(COOKIE_FILE) > 10:
            opts["cookiefile"] = COOKIE_FILE
        return opts

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            search = VideosSearch(link, limit=1)
            import inspect
            if inspect.iscoroutinefunction(search.next):
                result = (await search.next())["result"]
            else:
                result = search.result()["result"]
                
            if not result:
                return "Unknown", "00:00", 0, "https://telegra.ph/file/default.jpg", "None"
            
            res = result[0]
            title = res.get("title", "Unknown")
            duration = res.get("duration", "00:00")
            thumb = res["thumbnails"][0]["url"].split("?")[0]
            vidid = res.get("id", "None")
            
            seconds = 0
            if duration:
                try:
                    parts = duration.split(':')
                    for i, part in enumerate(reversed(parts)):
                        seconds += int(part) * (60 ** i)
                except: seconds = 0
            
            return title, duration, seconds, thumb, vidid
        except Exception:
            return "Unknown", "00:00", 0, "https://telegra.ph/file/default.jpg", "None"

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """Direct Stream Link extraction with Anti-Ban Protection"""
        if videoid:
            link = self.base + link
        
        opts = self.get_ytdl_opts(is_video=True)
        try:
            loop = asyncio.get_running_loop()
            def extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    time.sleep(random.uniform(0.3, 0.8)) # Human delay
                    info = ydl.extract_info(link, download=False)
                    return info.get('url', None)
            
            url = await loop.run_in_executor(None, extract)
            if url:
                return 1, url
            return 0, "YouTube requires login or cookies expired."
        except Exception as e:
            return 0, str(e)

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        try:
            playlist = Playlist(link)
            if hasattr(playlist, 'next'):
                res = await playlist.next()
                return [v['id'] for v in res['result'][:limit]]
            else:
                return [v['id'] for v in playlist.videos[:limit]]
        except:
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        det = await self.details(link, videoid)
        track_details = {
            "title": det[0],
            "link": self.base + det[4],
            "vidid": det[4],
            "duration_min": det[1],
            "thumb": det[3],
        }
        return track_details, det[4]

    async def download(
        self,
        link: str,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        **kwargs
    ) -> str:
        """Pure Streaming extraction using Cookies & Client Bypass."""
        if videoid:
            link = self.base + link
        
        loop = asyncio.get_running_loop()

        def _get_stream():
            opts = self.get_ytdl_opts(is_video=bool(video))
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return info['url']

        try:
            stream_url = await loop.run_in_executor(None, _get_stream)
            return stream_url, None
        except Exception as e:
            # Fallback message for UI
            error_text = str(e)
            if "Sign in to confirm" in error_text:
                return "YouTube blocked this request. Please update cookies.txt", False
            return error_text, False
