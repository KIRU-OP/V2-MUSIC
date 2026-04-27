from pyrogram.types import InlineKeyboardButton
import config
from AnonXMusic import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", 
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(
                text="✨ sᴜᴩᴩᴏʀᴛ ✨", 
                url=config.SUPPORT_CHAT
            ),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text="ʜᴇʟᴩ & ᴄᴏᴍᴍᴀɴᴅs", 
                callback_data="settings_back_helper"
            )
        ],
        [
            InlineKeyboardButton(text="❄ ᴄʜᴀɴɴᴇʟ ❄", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="✨ sᴜᴩᴩᴏʀᴛ ✨", url=config.SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(
                text="☁️ sᴏᴜʀᴄᴇ ☁️", url="https://t.me/about_deadly_venom"
            ),
            InlineKeyboardButton(text="🥀 ᴅᴇᴠᴇʟᴏᴩᴇʀ 🥀", user_id=config.OWNER_ID),
        ],
    ]
    return buttons
