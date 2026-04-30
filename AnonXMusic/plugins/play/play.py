from pyrogram import filters
from pyrogram.types import Message
import config
from AnonXMusic import Saavn, Telegram, app
from AnonXMusic.utils import seconds_to_min
from AnonXMusic.utils.decorators.play import PlayWrapper
from AnonXMusic.utils.logger import play_logs
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS

@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay"])
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    mystic = await message.reply_text("🔎 **JioSaavn se dhoondh raha hoon...**")
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Check Telegram File
    audio_tg = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    if audio_tg:
        file_path = await Telegram.get_filepath(audio=audio_tg)
        if await Telegram.download(_, message, mystic, file_path):
            details = {"title": "Telegram File", "link": "https://t.me/telegram", "path": file_path, "dur": audio_tg.duration}
            await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, streamtype="telegram", forceplay=fplay)
            return

    # Get Search Query
    query = url if url else (message.text.split(None, 1)[1] if len(message.command) > 1 else None)
    if not query:
        return await mystic.edit_text("❌ Gaane ka naam likhein ya JioSaavn link dein.")

    # Saavn Search
    try:
        res = await Saavn.get_link(query)
        if not res:
            return await mystic.edit_text("❌ JioSaavn par gaana nahi mila!")
        
        title, duration, thumb, stream_url = res
        
        if duration > config.DURATION_LIMIT:
            return await mystic.edit_text(f"❌ Gaana bahut bada hai. Limit {config.DURATION_LIMIT_MIN} minute hai.")

        details = {
            "title": title,
            "link": stream_url,
            "thumb": thumb,
            "duration_min": seconds_to_min(duration),
        }

        await stream(
            _, mystic, user_id, details, chat_id, user_name,
            message.chat.id, video=video, streamtype="saavn", forceplay=fplay
        )
        
        await mystic.delete()
        return await play_logs(message, streamtype="JioSaavn Only")

    except Exception as e:
        await mystic.edit_text(f"❌ Error: {e}")