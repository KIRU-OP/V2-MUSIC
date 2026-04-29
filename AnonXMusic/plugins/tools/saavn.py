import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AnonXMusic import app
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS
from AnonXMusic.utils.decorators.play import PlayWrapper

# JioSaavn API URL
JIOSAAVN_API = "https://jiosaavn-api.pashivam584.workers.dev"

# --- Helper Functions ---

async def jiosaavn_search(query: str):
    """JioSaavn se gaana search karne ke liye"""
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
    """Best quality audio link nikalne ke liye"""
    download_urls = song.get("downloadUrl", [])
    if not download_urls:
        return None
    # Best quality priority
    qualities = ["320kbps", "160kbps", "96kbps"]
    url_map = {item.get("quality"): item.get("url") for item in download_urls}
    for q in qualities:
        if q in url_map:
            return url_map[q]
    return download_urls[-1].get("url") if download_urls else None

# --- Play Command ---

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
    """Gaana search karke direct VC mein play karne ke liye"""
    if len(message.command) < 2:
        return await message.reply_text("🔎 **Kripya gaane ka naam likhein!**\nExample: `/saavn Pehle Bhi Main`")

    query = message.text.split(None, 1)[1]
    mystic = await message.reply_text(f"🔍 Searching **{query}** on JioSaavn...")

    song = await jiosaavn_search(query)
    if not song:
        return await mystic.edit("❌ Gaana nahi mila.")

    audio_url = get_best_audio(song)
    if not audio_url:
        return await mystic.edit("❌ Is gaane ka link nahi mil paya.")

    # --- Standard Stream Function (Positional Arguments Only) ---
    # Naye AnonXMusic versions mein keywords ('title=', etc.) error dete hain
    # Isliye hum sirf values bhej rahe hain
    try:
        await stream(
            _,                  # client
            mystic,             # processing message
            message.from_user.id, # user id
            audio_url,          # link
            message.chat.id,    # chat id
            message.from_user.mention, # user name
            message.chat.id,    # original chat id
            None,               # video (None for audio)
            "audio",            # streamtype
        )
    except Exception as e:
        await mystic.edit(f"❌ Error while streaming: {e}")
        return

    # Delete 'searching' message after successful stream start
    try:
        await mystic.delete()
    except:
        pass


@app.on_message(filters.command(["saavninfo"]) & ~BANNED_USERS)
async def saavn_info(_, message: Message):
    """Sirf gaane ki details dekhne ke liye"""
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/saavninfo [song name]`")

    query = message.text.split(None, 1)[1]
    song = await jiosaavn_search(query)
    
    if not song:
        return await message.reply_text("❌ Gaana nahi mila.")

    title = song.get("name")
    album = song.get("album", {}).get("name", "N/A")
    audio = get_best_audio(song)
    image = song.get("image", [])[-1].get("url") if song.get("image") else None

    caption = (
        f"🎵 **Title:** {title}\n"
        f"💿 **Album:** {album}\n\n"
        f"🚀 **Powered by JioSaavn**"
    )
    
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Download Audio", url=audio)]])
    
    if image:
        await message.reply_photo(image, caption=caption, reply_markup=buttons)
    else:
        await message.reply_text(caption, reply_markup=buttons)
