import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AnonXMusic import app
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS
from AnonXMusic.utils.decorators.play import PlayWrapper

# API Configuration
JIOSAAVN_API = "https://jiosaavn-api.pashivam584.workers.dev"

# --- JioSaavn Helper Functions ---

async def jiosaavn_search(query: str):
    """JioSaavn API se gaana search karne ke liye"""
    url = f"{JIOSAAVN_API}/api/search/songs"
    params = {"query": query, "page": 1, "limit": 1}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                results = data.get("data", {}).get("results", [])
                return results[0] if results else None
    except Exception:
        return None

def get_best_audio(song):
    """Sabse acchi quality (320kbps) ka link nikalne ke liye"""
    download_urls = song.get("downloadUrl", [])
    if not download_urls:
        return None
    # Quality Priority: 320 -> 160 -> 96
    qualities = ["320kbps", "160kbps", "96kbps"]
    url_map = {item.get("quality"): item.get("url") for item in download_urls}
    for q in qualities:
        if q in url_map:
            return url_map[q]
    return download_urls[-1].get("url") if download_urls else None

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
    fplay,      # 7th Arg
    queue,      # 8th Arg
    config      # 9th Arg
):
    """JioSaavn se gaana dhoond kar VC mein play karne ke liye"""
    if len(message.command) < 2:
        return await message.reply_text("🔎 **Kripya gaane ka naam likhein!**\nExample: `/saavn Pehle Bhi Main`")

    query = message.text.split(None, 1)[1]
    mystic = await message.reply_text(f"🔍 Searching **{query}** on JioSaavn...")

    # Search step
    song = await jiosaavn_search(query)
    if not song:
        return await mystic.edit("❌ Gaana nahi mila, kripya sahi spelling check karein.")

    # Details extraction
    title = song.get("name", "Unknown Saavn Song")
    audio_url = get_best_audio(song)
    duration_sec = int(song.get("duration", 0))
    thumb = song.get("image", [])[-1].get("url") if song.get("image") else None
    vidid = song.get("id") 
    
    if not audio_url:
        return await mystic.edit("❌ Is gaane ka link nahi mil paya.")

    # Time format conversion (MM:SS)
    minutes, seconds = divmod(duration_sec, 60)
    duration_str = f"{minutes:02d}:{seconds:02d}"

    # --- Stream Function Call (Cleaned for your version) ---
    try:
        await stream(
            _,
            mystic,
            message.from_user.id,
            audio_url,           # Direct Saavn Link
            message.chat.id,
            message.from_user.mention,
            message.chat.id,
            video=None,
            streamtype="audio",
            title=title,
            duration=duration_str,
            thumb=thumb,
            vidid=vidid,
        )
    except Exception as e:
        await mystic.edit(f"❌ Streaming Error: {e}")
        return

    # Success: Delete the searching message
    try:
        await mystic.delete()
    except:
        pass


@app.on_message(filters.command(["saavninfo"]) & ~BANNED_USERS)
async def saavn_info(_, message: Message):
    """Gaane ki info aur download link display karne ke liye"""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/saavninfo [song name]`")

    query = message.text.split(None, 1)[1]
    song = await jiosaavn_search(query)
    
    if not song:
        return await message.reply_text("❌ Gaana nahi mila.")

    title = song.get("name")
    album = song.get("album", {}).get("name", "N/A")
    artist = song.get("artists", {}).get("primary", [{}])[0].get("name", "N/A")
    audio = get_best_audio(song)
    image = song.get("image", [])[-1].get("url") if song.get("image") else None

    caption = (
        f"🎵 **Title:** {title}\n"
        f"👤 **Artist:** {artist}\n"
        f"💿 **Album:** {album}\n\n"
        f"🚀 **Powered by JioSaavn**"
    )
    
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download Audio", url=audio)]])
    
    if image:
        await message.reply_photo(image, caption=caption, reply_markup=buttons)
    else:
        await message.reply_text(caption, reply_markup=buttons)
