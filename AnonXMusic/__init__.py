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

# Direct Imports (Taaki NameError kabhi na aaye)
from AnonXMusic.platforms.Apple import AppleAPI
from AnonXMusic.platforms.Carbon import CarbonAPI
from AnonXMusic.platforms.Saavn import SaavnAPI
from AnonXMusic.platforms.Soundcloud import SoundAPI
from AnonXMusic.platforms.Spotify import SpotifyAPI
from AnonXMusic.platforms.Resso import RessoAPI
from AnonXMusic.platforms.Telegram import TeleAPI
from AnonXMusic.platforms.Youtube import YouTubeAPI

# Initialize instances
Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
Saavn = SaavnAPI()

# Compatibility Aliases (Bot ke baaki parts ke liye)
JioSaavn = Saavn
Jiosabun = Saavn
