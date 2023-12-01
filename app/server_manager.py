import random

from requests import get, post

from test_map import mas
from requests.exceptions import ConnectionError


class ServerManager:

    def __init__(self, config):
        self.server_name = ""
        self.config = config

    def get_world(self):
        params = {
            "name": self.server_name,
            # "player_name": player_name
        }
        try:
            return get(f"{self.config['host']}/get_world", params=params).json()["world"]
        except ConnectionError:
            return False

    def connect_user(self, player_name):
        params = {
            "name": self.server_name,
            "player_name": player_name
        }
        try:
            out = post(f"{self.config['host']}/connect_user", params=params).json()
            if out["status"] == "ok":
                return True
            return False
        except ConnectionError:
            return False

    def update_user(self, player_name, pos, hpr):
        params = {
            "name": self.server_name,
            "player_name": player_name,
            "x": pos.x,
            "y": pos.y,
            "z": pos.z,
            "h": hpr.x,
            "p": hpr.y,
            "r": hpr.z,
        }
        try:
            out = get(f"{self.config['host']}/update_user", params=params).json()
            if out["status"] == "no health":
                return True
            return False
        except ConnectionError:
            return False

    def respawn_user(self, player_name):
        params = {
            "name": self.server_name,
            "player_name": player_name,
        }
        try:
            out = get(f"{self.config['host']}/respawn_user", params=params).json()
            if out["status"] == "ok":
                return out["x"], out["y"], out["z"]
        except ConnectionError:
            return False

    def hit_player(self, player_name):
        params = {
            "name": self.server_name,
            "player_name": player_name,
        }
        try:
            post(f"{self.config['host']}/hit_user", params=params)
        except ConnectionError:
            return False

    def disconnect_user(self, player_name):
        params = {
            "name": self.server_name,
            "player_name": player_name
        }
        try:
            out = post(f"{self.config['host']}/disconnect_user", params=params).json()
            if out["status"] == "ok":
                return True
            return False
        except ConnectionError:
            return False

    def set_block(self, player_name, item_name, pos):
        params = {
            "name": self.server_name,
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "player_name": player_name,
            "item_name": item_name
        }
        try:
            post(f"{self.config['host']}/set_block", params=params)
        except ConnectionError:
            return False

    def pop_block(self, player_name, pos):
        params = {
            "name": self.server_name,
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "player_name": player_name
        }
        try:
            post(f"{self.config['host']}/remove_block", params=params)
        except ConnectionError:
            return False

    def create_server(self):
        r = random.randint(0, 10000)
        r = 130
        # print(r)
        params = {
            "name": f"First {r}",
        }
        self.server_name = f"First {r}"

        # 28 code
        # for i in range(60):
        try:
            return get(f"{self.config['host']}/create_server", params=params).json()
        except ConnectionError:
            return
