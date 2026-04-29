import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AnonXMusic import app
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS
from AnonXMusic.utils.decorators.play import PlayWrapper

# API Configuration
JIOSAAVN_API = "https://jiosaavn-api.pashivam584.workers.dev"

# --- Helper Functions ---

async def jiosaavn_search(query: str):
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
    download_urls = song.get("downloadUrl", [])
    if not download_urls:
        return None
    # Priority: 320kbps -> 160kbps -> 96kbps
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
    fplay, 
    queue, 
    config
):
    if len(message.command) < 2:
        return await message.reply_text("🔎 **Kripya gaane ka naam likhein!**\nExample: `/saavn Pehle Bhi Main`")

    query = message.text.split(None, 1)[1]
    mystic = await message.reply_text(f"🔍 Searching **{query}** on JioSaavn...")

    # Search Song
    song = await jiosaavn_search(query)
    if not song:
        return await mystic.edit("❌ Gaana nahi mila.")

    # Extract Data
    title = song.get("name", "Saavn Song")
    audio_url = get_best_audio(song)
    duration_sec = int(song.get("duration", 0))
    thumb = song.get("image", [])[-1].get("url") if song.get("image") else None
    
    if not audio_url:
        return await mystic.edit("❌ Is gaane ka link nahi mil paya.")

    # Format Duration
    minutes, seconds = divmod(duration_sec, 60)
    duration_str = f"{minutes:02d}:{seconds:02d}"

    # --- Final Stream Call (Exactly 11 Positional Arguments) ---
    # Hum keywords (title=) nahi use kar rahe taaki crash na ho.
    # Hum exact 11 arguments bhej rahe hain jo Assistant join karne ke liye zaroori hain.
    try:
        await stream(
            _,                  # 1. client
            mystic,             # 2. processing message
            message.from_user.id, # 3. user_id
            audio_url,          # 4. audio link
            message.chat.id,    # 5. chat_id
            message.from_user.mention, # 6. user_name
            message.chat.id,    # 7. original_chat_id
            None,               # 8. video (None)
            "audio",            # 9. streamtype
            title,              # 10. title (Assistant info)
            duration_str,       # 11. duration (Assistant info)
        )
    except Exception as e:
        await mystic.edit(f"❌ Streaming Error: {e}")
        return

    # Success: Delete searching message
    try:
        await mystic.delete()
    except:
        pass


@app.on_message(filters.command(["saavninfo"]) & ~BANNED_USERS)
async def saavn_info(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/saavninfo [song name]`")
    query = message.text.split(None, 1)[1]
    song = await jiosaavn_search(query)
    if not song: return await message.reply_text("❌ Not found.")
    
    audio = get_best_audio(song)
    await message.reply_photo(
        photo=song.get("image", [])[-1].get("url"),
        caption=f"🎵 **{song.get('name')}**\n🚀 JioSaavn Search",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download", url=audio)]])
    )
