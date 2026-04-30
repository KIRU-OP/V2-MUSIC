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
    # Search Query nikalna
    if url:
        query = url
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    else:
        return await message.reply_text("❌ Gaane ka naam likhein.")

    mystic = await message.reply_text(f"🔎 Searching **{query}** on JioSaavn...")

    try:
        # Saavn API call
        res = await Saavn.get_link(query)
        if not res:
            return await mystic.edit_text("❌ JioSaavn par gaana nahi mila! Dubara koshish karein.")
        
        title, duration, thumb, stream_url = res
        
        details = {
            "title": title,
            "link": stream_url,
            "thumb": thumb,
            "duration_min": seconds_to_min(duration),
        }

        # Play Stream
        await stream(
            _, mystic, message.from_user.id, details, chat_id, 
            message.from_user.first_name, message.chat.id, 
            video=video, streamtype="saavn", forceplay=fplay
        )
        await mystic.delete()

    except Exception as e:
        await mystic.edit_text(f"❌ Error: {e}")
