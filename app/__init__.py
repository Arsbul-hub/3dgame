import json

from app.collision import Collision
from app.server_manager import ServerManager
from app.sound_manager import SoundManager

with open("config.json", "r") as f:
    config = json.load(f)
server_manager = ServerManager(config)
collision_manager = Collision()
sound_manager = SoundManager()
