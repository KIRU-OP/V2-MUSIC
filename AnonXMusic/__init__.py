from AnonXMusic.core.bot import Anony
from AnonXMusic.core.dir import dirr
from AnonXMusic.core.git import git
from AnonXMusic.core.userbot import Userbot
from AnonXMusic.misc import dbb, heroku

from .logging import LOGGER

# Initialize directories, git, database, and heroku
dirr()
git()
dbb()
heroku()

# Initialize Bot and Userbot
app = Anony()
userbot = Userbot()

# Import Platform APIs
from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
# Correct the class name if necessary (usually SaavnAPI or JioSaavnAPI)
JioSaavn = SaavnAPI()
