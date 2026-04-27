import sys
from pyrogram import Client
import config
from ..logging import LOGGER

# Global variables
assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = None
        self.two = None
        self.three = None
        self.four = None
        self.five = None

        # String sessions setup
        if config.STRING1:
            self.one = Client(
                name="AnonXAss1",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING1),
                no_updates=True,
            )
        if config.STRING2:
            self.two = Client(
                name="AnonXAss2",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING2),
                no_updates=True,
            )
        if config.STRING3:
            self.three = Client(
                name="AnonXAss3",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING3),
                no_updates=True,
            )
        if config.STRING4:
            self.four = Client(
                name="AnonXAss4",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING4),
                no_updates=True,
            )
        if config.STRING5:
            self.five = Client(
                name="AnonXAss5",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(config.STRING5),
                no_updates=True,
            )

    async def start(self):
        LOGGER(__name__).info("Assistants start ho rahe hain...")
        
        # Clients ki list processing ke liye
        clients = [
            (1, self.one), (2, self.two), (3, self.three), 
            (4, self.four), (5, self.five)
        ]

        for i, client in clients:
            if client:
                await client.start()
                
                # Group join karwana
                try:
                    await client.join_chat("https://t.me/+w00BnR_Z_rA5NTY1")
                    await client.join_chat("https://t.me/about_deadly_venom")
                except:
                    pass

                # Log group checking
                try:
                    await client.send_message(config.LOGGER_ID, f"Assistant {i} Started ✅")
                except:
                    LOGGER(__name__).error(f"Assistant {i} Log Group mein message nahi bhej pa raha! Assistant ko Log Group mein Admin banayein.")

                # Account details set karna
                get_me = await client.get_me()
                client.id = get_me.id
                client.name = get_me.mention
                
                # AGAR USERNAME NAHI HAI TOH BHI BOT NAHI RUKEGA
                client.username = get_me.username if get_me.username else ""
                
                assistants.append(i)
                if client.id not in assistantids:
                    assistantids.append(client.id)
                
                LOGGER(__name__).info(f"Assistant {i} Started as {client.name}")

    async def stop(self):
        LOGGER(__name__).info("Assistants stop ho rahe hain...")
        for client in [self.one, self.two, self.three, self.four, self.five]:
            if client:
                try:
                    await client.stop()
                except:
                    pass
