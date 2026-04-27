import sys
from pyrogram import Client
import config
from ..logging import LOGGER

# Global lists
assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = None
        self.two = None
        self.three = None
        self.four = None
        self.five = None

        # String sessions ki list
        strings = [config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]
        
        # Clients ko initialize karna
        for i, session in enumerate(strings, start=1):
            if session:
                client = Client(
                    name=f"AnonXAss{i}",
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=str(session),
                    no_updates=True,
                )
                # Dynamic attribute set karna (self.one, self.two, etc.)
                if i == 1: self.one = client
                elif i == 2: self.two = client
                elif i == 3: self.three = client
                elif i == 4: self.four = client
                elif i == 5: self.five = client

    async def start(self):
        LOGGER(__name__).info("Assistant(s) start ho rahe hain...")
        
        # Ek list banate hain sirf un clients ki jo config mein diye gaye hain
        active_clients = []
        if self.one: active_clients.append((1, self.one))
        if self.two: active_clients.append((2, self.two))
        if self.three: active_clients.append((3, self.three))
        if self.four: active_clients.append((4, self.four))
        if self.five: active_clients.append((5, self.five))

        for i, client in active_clients:
            await client.start()
            
            # Group join karwane ka logic
            try:
                await client.join_chat("https://t.me/+w00BnR_Z_rA5NTY1")
                await client.join_chat("https://t.me/about_deadly_venom")
            except Exception:
                pass

            # Log group access check
            try:
                await client.send_message(config.LOGGER_ID, f"Assistant {i} Started")
            except Exception:
                LOGGER(__name__).error(
                    f"Assistant Account {i} failed to access the Log Group. "
                    f"Make sure you have added assistant {i} to your log group and promoted as admin!"
                )
                sys.exit()

            # Details fetch aur set karna
            get_me = await client.get_me()
            client.id = get_me.id
            client.name = get_me.mention
            client.username = get_me.username
            
            if not client.username:
                LOGGER(__name__).error(f"Assistant {i} ka username missing hai. Please username set karein aur restart karein.")
                sys.exit()

            assistants.append(i)
            if client.id not in assistantids:
                assistantids.append(client.id)
                
            LOGGER(__name__).info(f"Assistant {i} Started as {client.name}")

    async def stop(self):
        LOGGER(__name__).info("Assistant(s) stop ho rahe hain...")
        clients_to_stop = [self.one, self.two, self.three, self.four, self.five]
        for client in clients_to_stop:
            if client:
                try:
                    await client.stop()
                except Exception:
                    pass
