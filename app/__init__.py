import json

from app.collision import Collision
from app.server_manager import ServerManager

with open("config.json", "r") as f:
    config = json.load(f)
server_manager = ServerManager(config)
collision_manager = Collision()
