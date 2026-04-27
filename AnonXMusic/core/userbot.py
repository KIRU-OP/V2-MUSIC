import sys
from pyrogram import Client
from pyrogram.errors import (
    PeerIdInvalid,
    ChatIdInvalid,
    UserNotParticipant,
    UsernameNotOccupied,
    InviteHashExpired,
    UserAlreadyParticipant,
    InviteRequestSent,
    RPCError,
)
# Config aur Logging imports
import config
from ..logging import LOGGER

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        # Clients define kar rahe hain
        self.one = self._create_client(config.STRING1, "AnonXAss1")
        self.two = self._create_client(config.STRING2, "AnonXAss2")
        self.three = self._create_client(config.STRING3, "AnonXAss3")
        self.four = self._create_client(config.STRING4, "AnonXAss4")
        self.five = self._create_client(config.STRING5, "AnonXAss5")

    def _create_client(self, string, name):
        if string:
            return Client(
                name=name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_string=str(string),
                no_updates=True,
            )
        return None

    async def _start_assistant(self, client, assistant_num):
        if not client:
            return

        try:
            await client.start()
            
            # Assistant ki info nikalna
            get_me = await client.get_me()
            client.id = get_me.id
            client.name = get_me.mention
            
            # FIX: Agar username nahi hai to empty string rakhein, None nahi
            client.username = get_me.username if get_me.username else ""
            
            # --- LOGGER GROUP JOIN LOGIC ---
            if config.LOGGER_ID:
                try:
                    await client.join_chat(config.LOGGER_ID)
                    LOGGER(__name__).info(f"✅ Assistant {assistant_num} joined Logger Group.")
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    LOGGER(__name__).error(f"❌ Assistant {assistant_num} Logger join nahi kar paya: {e}")

            assistants.append(assistant_num)
            if client.id not in assistantids:
                assistantids.append(client.id)
                
            LOGGER(__name__).info(f"✅ Assistant {assistant_num} Started as {client.name}")

        except Exception as e:
            LOGGER(__name__).error(f"🚫 Assistant {assistant_num} Start Error: {e}")

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")
        
        # Individual starts with error safety
        if self.one:
            await self._start_assistant(self.one, 1)
        if self.two:
            await self._start_assistant(self.two, 2)
        if self.three:
            await self._start_assistant(self.three, 3)
        if self.four:
            await self._start_assistant(self.four, 4)
        if self.five:
            await self._start_assistant(self.five, 5)

        if not assistants:
            LOGGER(__name__).error("🚫 Koi bhi assistant start nahi hua. Please check your STRING sessions.")
            sys.exit()

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        clients = [self.one, self.two, self.three, self.four, self.five]
        for client in clients:
            if client:
                try:
                    await client.stop()
                except Exception:
                    pass
