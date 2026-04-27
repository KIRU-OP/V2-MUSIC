from pyrogram import Client
import config
from ..logging import LOGGER

# Global variables
assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        # Initializing attributes to None
        self.one = None
        self.two = None
        self.three = None
        self.four = None
        self.five = None

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")
        
        # Mapping config strings to their respective attribute names and numbers
        sessions = [
            (config.STRING1, "one", 1),
            (config.STRING2, "two", 2),
            (config.STRING3, "three", 3),
            (config.STRING4, "four", 4),
            (config.STRING5, "five", 5),
        ]

        for string, attr_name, index in sessions:
            if string:
                # Client initialization
                client = Client(
                    name=f"DilXAss{index}",
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=str(string),
                    no_updates=True,
                )
                # Setting self.one, self.two, etc.
                setattr(self, attr_name, client)
                
                try:
                    await client.start()
                    
                    # Support Chat Join Karna
                    try:
                        await client.join_chat("NOBITA_SUPPORT")
                    except Exception:
                        pass
                    
                    # Logger Group Permission Check
                    try:
                        await client.send_message(config.LOGGER_ID, f"Assistant {index} Started ✅")
                    except Exception as e:
                        LOGGER(__name__).error(
                            f"Assistant Account {index} failed to access log group ({config.LOGGER_ID}). "
                            f"Reason: {e}. Make sure it's an admin!"
                        )
                        # Agar aap chahte hain ki error aane par bot band na ho, 
                        # toh niche wali 'exit()' line ko comment (#) kar dein.
                        # exit() 

                    # Client details save karna
                    me = await client.get_me()
                    client.id = me.id
                    client.name = me.mention
                    client.username = me.username
                    
                    # Adding to global lists
                    assistants.append(index)
                    assistantids.append(client.id)
                    
                    LOGGER(__name__).info(f"Assistant {index} Started as {client.name}")

                except Exception as e:
                    LOGGER(__name__).error(f"Assistant {index} failed to start: {str(e)}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        # Check all possible assistant attributes and stop them
        for attr_name in ["one", "two", "three", "four", "five"]:
            client = getattr(self, attr_name)
            if client:
                try:
                    await client.stop()
                except Exception:
                    pass
