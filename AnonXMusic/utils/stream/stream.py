import os
from pyrogram.types import InlineKeyboardMarkup
import config
from AnonXMusic import app
from AnonXMusic.core.call import Anony
from AnonXMusic.misc import db
from AnonXMusic.utils.database import is_active_chat
from AnonXMusic.utils.inline import aq_markup, stream_markup
from AnonXMusic.utils.stream.queue import put_queue
from AnonXMusic.utils.thumbnails import get_thumb

async def stream(
    _, mystic, user_id, result, chat_id, user_name, original_chat_id,
    video=None, streamtype=None, spotify=None, forceplay=None,
):
    if not result:
        return
    if forceplay:
        await Anony.force_stop_stream(chat_id)

    # ────── JIOSAAVN BADA MESSAGE LOGIC ──────
    if streamtype == "saavn":
        file_path = result["path"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        vidid = result["videoid"]
        
        if await is_active_chat(chat_id):
            # Queue mein daalne ke liye
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, vidid, user_id, "video" if video else "audio")
            position = len(db.get(chat_id)) - 1
            await app.send_message(original_chat_id, text=f"📝 **Queued at {position}:** {title[:25]}", reply_markup=InlineKeyboardMarkup(aq_markup(_, chat_id)))
        else:
            if not forceplay:
                db[chat_id] = []
            
            # VC Join karna (file_path string hona chahiye)
            await Anony.join_call(chat_id, original_chat_id, file_path, video=video, image=thumbnail)
            await put_queue(chat_id, original_chat_id, file_path, title, duration_min, user_name, vidid, user_id, "video" if video else "audio", forceplay=forceplay)
            
            # --- BADA PHOTO MESSAGE BHEJNA ---
            try:
                img = await get_thumb(vidid, user_id, title, duration_min, thumbnail)
            except:
                img = thumbnail # Failover to original thumb

            run = await app.send_photo(
                original_chat_id,
                photo=img,
                caption=f"✨ **Now Playing**\n\n📌 **Title:** {title[:25]}\n👤 **Requested By:** {user_name}",
                reply_markup=InlineKeyboardMarkup(stream_markup(_, chat_id)),
            )
            db[chat_id][0]["mystic"] = run
        
        if mystic:
            await mystic.delete()
        return
    # ────── JIOSAAVN END ──────

    # (Yahan aapki purani YouTube aur Telegram logic reh sakti hai...)
