import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AnonXMusic import app
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS
from AnonXMusic.utils.decorators.play import PlayWrapper

# JioSaavn API Configuration
JIOSAAVN_API = "https://jiosaavn-api.pashivam584.workers.dev"

# --- Helper: Gaana Search Karne Ke Liye ---
async def jiosaavn_search(query: str):
    url = f"{JIOSAAVN_API}/api/search/songs"
    params = {"query": query, "page": 1, "limit": 1}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                # Check status and results
                if data.get("status") == "SUCCESS":
                    results = data.get("data", {}).get("results", [])
                    return results[0] if results else None
                return None
    except Exception:
        return None

# --- Helper: Best Quality Link Nikalne Ke Liye ---
def get_best_audio(song):
    if not song: return None
    download_urls = song.get("downloadUrl", [])
    if not download_urls: return None
    
    # Best Quality (320kbps) pehle check karega
    qualities = ["320kbps", "160kbps", "96kbps"]
    url_map = {item.get("quality"): item.get("url") for item in download_urls}
    
    for q in qualities:
        if q in url_map:
            return url_map[q]
    return download_urls[-1].get("url")

# --- Main Play Command ---

@app.on_message(filters.command(["saavn", "jsaavn"]) & filters.group & ~BANNED_USERS)
@PlayWrapper
async def saavn_play(
    _, 
    message: Message, 
    streamtype, 
    lang, 
    streamer, 
    forceplay, 
    fplay,      
    queue,      
    config      
):
    """Voice Chat mein JioSaavn gaana play karne ke liye"""
    if len(message.command) < 2:
        return await message.reply_text("🔎 **Kripya gaane ka naam likhein!**\nExample: `/saavn Kesariya`")

    query = message.text.split(None, 1)[1]
    mystic = await message.reply_text(f"🔍 Searching **{query}** on JioSaavn...")

    # 1. Search Result
    song = await jiosaavn_search(query)
    if not song:
        return await mystic.edit("❌ Gaana nahi mila, kripya spelling check karein.")

    # 2. Get Audio URL
    audio_url = get_best_audio(song)
    if not audio_url:
        return await mystic.edit("❌ Is gaane ka play link nahi mil paya.")

    title = song.get("name", "JioSaavn Stream")
    user_name = message.from_user.mention

    # 3. Trigger Streaming (Assistant Voice Chat join karega)
    try:
        await stream(
            _,                      # Client
            mystic,                 # Status message
            message.from_user.id,   # User ID
            audio_url,              # Direct Link (Saavn)
            message.chat.id,        # Chat ID
            user_name,              # Name
            message.chat.id,        # Original Chat ID
            None,                   # Video (None for audio)
            "index",                # 🔥 FIXED: 'index' use karein direct links ke liye
            None,                   # Spotify
            forceplay,              # Forceplay check
        )
    except Exception as e:
        await mystic.edit(f"❌ Streaming Error: {e}")
        return

    # Success: Processing message delete karein
    try:
        await mystic.delete()
    except:
        pass


@app.on_message(filters.command(["saavninfo"]) & ~BANNED_USERS)
async def saavn_info(_, message: Message):
    """Gaane ki details dikhane ke liye"""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/saavninfo [song name]`")

    query = message.text.split(None, 1)[1]
    song = await jiosaavn_search(query)
    
    if not song:
        return await message.reply_text("❌ Gaana nahi mila.")

    title = song.get("name")
    artist = song.get("artists", {}).get("primary", [{}])[0].get("name", "N/A")
    audio = get_best_audio(song)
    image_list = song.get("image", [])
    image = image_list[-1].get("url") if image_list else None

    caption = (
        f"🎵 **Title:** {title}\n"
        f"👤 **Artist:** {artist}\n\n"
        f"🚀 **Powered by JioSaavn**"
    )
    
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download Audio", url=audio)]])
    
    if image:
        await message.reply_photo(image, caption=caption, reply_markup=buttons)
    else:
        await message.reply_text(caption, reply_markup=buttons)
