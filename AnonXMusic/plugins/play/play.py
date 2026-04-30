import re
from pyrogram import filters
from pyrogram.types import Message
import config
from AnonXMusic import Saavn, app
from AnonXMusic.utils import seconds_to_min
from AnonXMusic.utils.decorators.play import PlayWrapper
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS

@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce"])
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
        return await message.reply_text("❌ **Gaane ka naam ya JioSaavn link dein.**")

    mystic = await message.reply_text(f"🔎 **Searching {query} on JioSaavn...**")

    try:
        # Saavn se details nikalna
        res = await Saavn.get_link(query)
        if not res:
            return await mystic.edit_text("❌ **JioSaavn par gaana nahi mila!**")
        
        title, duration, thumb, stream_url = res
        
        # Details jo stream.py ko chahiye bada message bhejne ke liye
        details = {
            "title": title,
            "path": str(stream_url), 
            "videoid": re.sub(r"\W+", "", title)[:10], # Thumbnail ke liye ID
            "duration_min": seconds_to_min(duration),
            "thumb": thumb,
        }

        # Stream Play (Hamesha 'saavn' type bhejenge)
        await stream(
            _, 
            mystic, 
            message.from_user.id, 
            details, 
            chat_id, 
            message.from_user.first_name, 
            message.chat.id, 
            video=video, 
            streamtype="saavn", 
            forceplay=fplay
        )

    except Exception as e:
        print(f"Play Error: {e}")
        await mystic.edit_text(f"❌ **Error:** {e}")
