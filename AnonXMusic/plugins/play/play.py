import re
from pyrogram import filters
from pyrogram.types import Message
import config
from AnonXMusic import Saavn, Telegram, app
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
        return await message.reply_text("❌ Gaane ka naam likhein ya JioSaavn link dein.")

    mystic = await message.reply_text(f"🔎 Searching **{query}** on JioSaavn...")

    try:
        # Saavn API se details lana
        res = await Saavn.get_link(query)
        if not res:
            return await mystic.edit_text("❌ JioSaavn par gaana nahi mila!")
        
        title, duration, thumb, stream_url = res
        
        # Duration ko minutes mein convert karna (Thumb aur Message ke liye)
        dur_min = seconds_to_min(duration)
        
        # Videoid generate karna taaki thumbnail function trigger ho
        # Hum title se hi ek unique id bana lete hain
        clean_id = re.sub(r"\W+", "", str(title))[:10]

        # --- COMPLETE DETAILS FOR JIOSAAVN ---
        details = {
            "title": title,
            "link": stream_url,
            "path": str(stream_url), 
            "videoid": clean_id,
            "duration_min": dur_min,
            "thumb": thumb,
        }

        # PLAY LOGIC 
        # Note: streamtype="saavn" use karne se 'stream.py' bada photo message bhejega
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
        
        # Mystic delete yahan nahi karenge, stream function khud handles karta hai
        # Agar Assistant VC join nahi karta toh check karein 'streamtype' in stream.py

    except Exception as e:
        print(f"Play Error: {e}")
        await mystic.edit_text(f"❌ Error: {e}")
