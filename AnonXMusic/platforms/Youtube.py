# Powered by: Kiru_Op
# Pure Streaming Version - Anti-Ban (Mobile Simulation)
# No OAuth2 - No Manual Login

import asyncio
import os
import re
import random
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

COOKIE_FILE = os.path.join(SESSION_DIR, "autogen_cookies.txt")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        
        # Mobile User Agents (YouTube trusts these more than Desktop)
        self.user_agents = [
            "com.google.ios.youtube/19.29.1 (iPhone15,3; U; CPU iOS 17_5_1 like Mac OS X; en_US)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
            "com.google.android.youtube/19.25.39 (Linux; U; Android 14; en_US; Pixel 8)"
        ]

    def get_random_ip(self):
        """Random IP for Header Spoofing"""
        return ".".join(map(str, (random.randint(1, 254) for _ in range(4))))

    def get_ytdl_opts(self):
        """
        Anti-Bot Optimized Settings.
        Force 'ios' client for bypass without login.
        """
        return {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "cookiefile": COOKIE_FILE, # Automatic session management
            "headers": {
                "X-Forwarded-For": self.get_random_ip(),
                "Accept-Language": "en-US,en;q=0.9",
                "User-Agent": random.choice(self.user_agents),
                "Referer": "https://www.google.com/",
            },
            "extractor_args": {
                "youtube": {
                    # iOS aur Android clients block nahi hote as compared to 'web'
                    "player_client": ["ios", "android", "mweb"],
                    "player_skip": ["webpage", "configs"],
                    "skip": ["hls", "dash"]
                }
            }
        }

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

    async def title(self, link: str, videoid: Union[bool, str] = None):
        res = await self.details(link, videoid)
        return res[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """Direct Stream Link extraction with Guest Cookies"""
        if videoid:
            link = self.base + link
        opts = self.get_ytdl_opts()
        opts["format"] = "best[height<=720]/bestaudio"
        
        try:
            loop = asyncio.get_running_loop()
            def extract():
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    return info['url']
            url = await loop.run_in_executor(None, extract)
            return 1, url
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
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        **kwargs
    ) -> str:
        """
        Pure Streaming Mode: Extracts URL using automatic cookie management.
        """
        if videoid:
            link = self.base + link
        
        loop = asyncio.get_running_loop()

        def _get_stream():
            opts = self.get_ytdl_opts()
            if video:
                opts["format"] = "best[height<=720]/best"
            else:
                opts["format"] = "bestaudio/best"

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                return info['url']

        try:
            stream_url = await loop.run_in_executor(None, _get_stream)
            return stream_url, None
        except Exception as e:
            return str(e), False
