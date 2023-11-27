import asyncio
import json
import random
import time

import numpy as np
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBaseGlobal import aspect2d
from numba import jit, njit
from panda3d.core import *

from app import server_manager


def get_distance(pos1, pos2):
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2
    dx = max(x1, x2) - min(x1, x2)
    dy = max(y1, y2) - min(y1, y2)
    dz = max(z1, z2) - min(z1, z2)
    return (dx ** 2 + dy ** 2 + dz ** 2) ** .5


class World(DirectObject):
    current_world = []

    blocks_nodes = []
    current_entities = {}
    entities_nodes = {}

    player_added_blocks = []
    player_removed_blocks = []
    player_entity = {}

    def __init__(self, player_name):
        super().__init__()
        self.player_name = player_name

    def addBlock(self, position, block_type, broke_index, max_broke_index):
        def on_loads(block):
            collision = CollisionBox(Vec3(block.getX() + 0.5, block.getY() + 0.5, block.getZ() + 0.5), 0.5, 0.5, 0.5)
            block.reparentTo(render)
            block.setName(block_type)
            block.setTag("block", "1")
            block.setScale(1, 1, 1)
            block.setPos(position)

            main_texture = loader.loadTexture(f"./app/static/images/textures/{block_type}.png")
            main_layer = TextureStage('main_texture')
            #main_layer.setMode(TextureStage.MDecal1
            block.setTexture(main_texture, 1)
            # ts.setColor((1, 0, 0, 1))
            #print(broke_index,  max_broke_index)
            if broke_index < max_broke_index:
                #print(123)
                broke_texture = loader.loadTexture(f"./app/static/images/textures/broke_texture.png")
                second_layer = TextureStage('broke_texture')
                second_layer.setMode(TextureStage.MDecal)
                block.setTexture(second_layer, broke_texture)
            cnodePath = block.attachNewNode(CollisionNode(block_type))

            cnodePath.node().addSolid(collision)
            # cnodePath.show()

            self.blocks_nodes.append(block)

        block = loader.loadModel("models/box", callback=on_loads, blocking=False)

        # print(self.nodes[position])
        # self.d = 0
        self.current_world.append({"pos": [position.x, position.y, position.z], "block_type": block_type})

        return {"pos": [position.x, position.y, position.z], "block_type": block_type}

    def removeBlock(self, pos):
        block_data, node = self.get_block(pos)
        if block_data and node:
            self.blocks_nodes.remove(node)
            self.current_world.remove(block_data)
            node.remove_node()

    def addEntity(self, position, name, scale, hpr, health, max_health):
        sx, sy, sz = scale

        block = loader.loadModel("models/box")
        # collision = CollisionBox(Vec3(block.getX() + 0.5, block.getY() + 0.5, block.getZ() + 0.5), 0.5, 0.5, 0.5)
        block.reparentTo(render)

        block.setScale(scale)
        block.setName(f"{name}")

        block.setPos(position - Vec3(sx / 2, sy / 2, sz / 2))
        block.setTag("entity", name)
        block.setHpr(hpr)
        # tex = loader.loadTexture(self.block_types.get(block_type, ""))

        # cnodePath.show()
        # cnodePath = block.attachNewNode(CollisionNode(name))

        # cnodePath.node().addSolid(collision)
        self.entities_nodes[name] = block
        # print(self.nodes[position])
        # self.d = 0
        entity = {"pos": [position.x, position.y, position.z],
                  "name": name,
                  "hpr": [hpr[0], hpr[1], hpr[2]],
                  "health": health,
                  "max_health": max_health,
                  }
        self.current_entities[name] = entity

        return entity

    def removeEntity(self, name):

        entity, node = self.get_entity(name)
        if entity and node:
            self.entities_nodes.pop(name)
            self.current_entities.pop(name)
            node.remove_node()

    def update_world(self):
        # await task.pause(1)
        # while True:
        world = server_manager.get_world()

        to_set, to_remove = self.get_worlds_difference(world["world"])

        # print(to_set, to_remove)
        for block in to_set:
            x, y, z = block["pos"]

            self.addBlock(position=Vec3(float(x), float(y), float(z)),
                          block_type=block["type"],
                          broke_index=block["broke"],
                          max_broke_index=block["broke_index"])
        for block in to_remove:
            x, y, z = block["pos"]
            self.removeBlock(Vec3(x, y, z))
        self.current_world = world["world"]
        # print(world["entities"])
        to_set_entity, to_remove_entity = self.get_entities_difference(world["entities"])
        for entity in to_set_entity:
            x, y, z = entity["pos"]
            h, p, r = entity["hpr"]
            if entity["name"] != self.player_name:
                # print(123)
                x, y, z = entity["pos"]
                h, p, r = entity["hpr"]
                sx, sy, sz = entity["scale"]

                self.addEntity(position=Vec3(float(x), float(y), float(z)),
                               name=entity["name"],
                               hpr=Vec3(float(h), float(p), float(r)),
                               scale=(float(sx), float(sy), float(sz)),
                               health=entity["health"],
                               max_health=entity["max_health"])
            else:
                # print(entity)
                entity = {"pos": [x, y, z],
                          "name": entity["name"],
                          "hpr": [h, p, r],
                          "health": entity["health"],
                          "max_health": entity["max_health"],
                          "inventory": entity["inventory"]
                          }
                self.player_entity = entity
        for entity in to_remove_entity:
            if entity["name"] != self.player_name:
                self.removeEntity(entity["name"])
        for name, entity in world["entities"].items():
            x, y, z = entity["pos"]
            h, p, r = entity["hpr"]
            sx, sy, sz = entity["scale"]
            # print(sx, sy, sz)
            if entity["name"] in self.current_entities:

                self.current_entities[name]["pos"] = Vec3(float(x), float(y), float(z))
                self.current_entities[name]["hpr"] = Vec3(float(h), float(p), float(r))
                self.current_entities[name]["health"] = float(entity["health"])
                if name in self.entities_nodes:
                    pos = Vec3(float(x), float(y), float(z)) - Vec3(float(sx) / 2, float(sy) / 2)
                    self.entities_nodes[name].setPos(pos)

        # print(self.current_entities)

        # d2 = time.time()
        # print(d2 - d1)
        # return task.cont

    def get_worlds_difference(self, world):

        set_blocks = np.array([])
        removed_blocks = np.array([])

        d1 = time.time()

        func_to_json = np.vectorize(lambda a: json.loads(a))

        world_new = np.array(
            list(map(lambda a: str(a).replace("\'", "\""), world)))
        world_old = np.array(list(
            map(lambda a: str(a).replace("\'", "\""),
                self.current_world)))
        set_blocks1 = np.setdiff1d(world_new, world_old)
        removed_blocks1 = np.setdiff1d(world_old, world_new)
        if set_blocks1.size:
            set_blocks = func_to_json(set_blocks1)
            set_blocks = set_blocks.tolist()
            set_blocks.sort(key=lambda a: get_distance(camera.getPos(), a["pos"]))
        if removed_blocks1.size:
            removed_blocks = func_to_json(removed_blocks1)
            removed_blocks = removed_blocks.tolist()
            removed_blocks.sort(key=lambda a: get_distance(camera.getPos(), a["pos"]))
        # print(removed_blocks)
        return set_blocks, removed_blocks

    def get_entities_difference(self, entities):
        set_entities = []
        removed_entities = []
        for name, entity in entities.items():
            if name not in self.current_entities.keys():
                set_entities.append(entity)
        for name, entity in self.current_entities.items():
            if name not in entities.keys():
                removed_entities.append(entity)

        # if removed_blocks1.size:
        #     removed_entities = func_to_json(removed_blocks1)
        #     removed_entities = removed_entities.tolist()
        #     removed_entities.sort(key=lambda a: get_distance(camera.getPos(), a["pos"]))

        return set_entities, removed_entities

    def get_block(self, block_pos):
        node = None
        block_data = None
        for block_node in self.blocks_nodes:

            if block_node.getPos() == block_pos:
                node = block_node
        for block in self.current_world:
            if block["pos"][0] == block_pos.x and block["pos"][1] == block_pos.y and block["pos"][2] == block_pos.z:
                block_data = block
        return block_data, node

    def get_entity(self, name):
        node = None
        entity_data = None
        # for entity_node in self.entities_nodes:
        #     if entity_node.getName() == f"Entity_{name}":
        #         node = entity_node
        # for entity in self.current_entities:
        #     if entity["name"] == name:
        #         entity_data = entity
        return self.current_entities.get(name), self.entities_nodes.get(name)

    def get_entity_by_pos(self, pos):
        node = None
        entity_data = None
        for entity_node in self.entities_nodes.values():
            if entity_node.getPos() == pos:
                node = entity_node
        for entity in self.current_entities.values():
            if entity["pos"] == pos:
                entity_data = entity
        return entity_data, node
