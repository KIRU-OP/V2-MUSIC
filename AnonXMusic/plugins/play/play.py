from pyrogram import filters
from pyrogram.types import Message
import config
from AnonXMusic import Saavn, Telegram, app
from AnonXMusic.utils import seconds_to_min
from AnonXMusic.utils.decorators.play import PlayWrapper
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS

@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay"])
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    if url:
        query = url
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("❌ Gaane ka naam likhein.")

    mystic = await message.reply_text(f"🔎 Searching **{query}** on JioSaavn...")

    try:
        # Saavn API se details lana
        res = await Saavn.get_link(query)
        if not res:
            return await mystic.edit_text("❌ JioSaavn par gaana nahi mila!")
        
        title, duration, thumb, stream_url = res
        
        # --- FIXED DETAILS FOR ANONX CORE ---
        # AnonX ka 'telegram' streamtype dictionary se 'path' (string) uthata hai.
        # Isse media_path error nahi aayega.
        details = {
            "title": title,
            "link": stream_url,
            "path": str(stream_url), # Path must be a string URL
            "dur": duration,
            "thumb": thumb,
        }

        # Stream Play (Using telegram streamtype to handle dictionary input)
        await stream(
            _, 
            mystic, 
            message.from_user.id, 
            details, 
            chat_id, 
            message.from_user.first_name, 
            message.chat.id, 
            video=video, 
            streamtype="telegram", 
            forceplay=fplay
        )
        await mystic.delete()

    except Exception as e:
        print(f"Play Error: {e}")
        await mystic.edit_text(f"❌ Error: {e}")
