import math
import sys
from math import *

import numpy as np
from direct.stdpy import thread
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from panda3d.core import CollisionNode
from panda3d.core import *

from app import server_manager


def degToRad(degrees):
    return degrees * (pi / 180.0)


def get_distance(pos1, pos2):
    x1, y1, z1 = pos1
    x2, y2, z2 = pos2
    dx = max(x1, x2) - min(x1, x2)
    dy = max(y1, y2) - min(y1, y2)
    dz = max(z1, z2) - min(z1, z2)
    return (dx ** 2 + dy ** 2 + dz ** 2) ** .5


class Player(DirectObject):
    name = None
    grounded = False
    h = 0
    p = 0
    r = 0
    is_jumping = False
    camera = None
    acceleration = 0.3
    max_acceleration = 0.4
    delta_z = 0
    playerMoveSpeed = 6
    keys = {}
    added_blocks = []
    removed_blocks = []
    can_move = True
    inventory = []
    current_inventory_item = 0

    def __init__(self, name, world, server_manager):
        super().__init__()
        self.world = world
        self.name = name
        self.server_manager = server_manager
        self.event_manager = CollisionHandlerQueue()
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler

        self.loadHitbox()
        self.setupMouseRay()
        self.setupGroundRay()
        self.setupPlayer()
        self.can_fall = False

    def disable_move(self):
        self.can_move = False

    def enable_move(self):
        self.can_move = True

    def setupGroundRay(self):
        ray = CollisionRay()
        ray.setOrigin(0, 0, -.2)
        ray.setDirection(0, 0, -1)
        cn = CollisionNode('playerRay')
        cn.addSolid(ray)
        cn.setFromCollideMask(BitMask32.bit(0))
        cn.setIntoCollideMask(BitMask32.allOff())
        self.solid = self.player.attachNewNode(cn)
        base.cTrav.addCollider(self.solid, self.event_manager)

    def setupMouseRay(self):
        pickerNode = CollisionNode('mouseRay')
        pickerNP = camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(pickerNP, self.pq)

        # self.picker.showCollisions(render)

    def loadHitbox(self):
        self.pusher = CollisionHandlerPusher()
        cs = CollisionBox((0, 0, .5), 0.25, 0.25, 1)  # CollisionCapsule(0, 0, 0, 0, 0, 0.3, 0.25)
        # cs.setCenter(0.7,0.7,0.7)
        self.player = render.attachNewNode(CollisionNode('player_hitbox'))
        self.player.node().addSolid(cs)
        self.player.setPos(10, 10, 20)
        self.pusher.addCollider(self.player, self.player)
        base.cTrav.addCollider(self.player, self.pusher)

    def setupPlayer(self):
        self.accept("w", self.swich_key, ["forward", True])
        self.accept("w-up", self.swich_key, ["forward", False])
        self.accept("s", self.swich_key, ["backward", True])
        self.accept("s-up", self.swich_key, ["backward", False])
        self.accept("d", self.swich_key, ["right", True])
        self.accept("d-up", self.swich_key, ["right", False])
        self.accept("a", self.swich_key, ["left", True])
        self.accept("a-up", self.swich_key, ["left", False])
        self.accept("space", self.swich_key, ["jump", True])
        self.accept("space-up", self.swich_key, ["jump", False])

        self.accept('mouse1', self.left_click)
        self.accept('mouse3', self.right_click)
        self.accept('wheel_up', self.set_inventory_item, [1])

        self.accept('wheel_down', self.set_inventory_item, [-1])

    def set_inventory_item(self, step):
        if self.inventory:
            if self.current_inventory_item + step == len(self.inventory):
                self.current_inventory_item = 0
            elif self.current_inventory_item + step < 0:
                self.current_inventory_item = len(self.inventory) - 1
            #print(self.inventory)

    def update_player(self, dt):
        # print(self.player.getPos())
        if self.can_move:
            if self.keys.get("forward"):
                self.move_player(dt, "forward")
            if self.keys.get("backward"):
                self.move_player(dt, "backward")
            if self.keys.get("right"):
                self.move_player(dt, "right")
            if self.keys.get("left"):
                self.move_player(dt, "left")
            if self.keys.get("jump"):
                self.jump()
            if self.can_fall:
                self.update_gravity(dt)
            if self.world.player_entity:
                self.inventory = self.world.player_entity["inventory"]
        #print(self.inventory)
    def update_pos(self):
        player_pos = Vec3(self.player.getX(), self.player.getY(), self.player.getZ() - 1)
        out = self.server_manager.update_user(self.name, player_pos, self.player.getHpr())

        if out:
            new_cords = self.server_manager.respawn_user(self.name)
            if new_cords:
                x, y, z = new_cords
                self.player.setPos(x, y, z)

    def move_player(self, dt, direction):
        x_movement = 0
        y_movement = 0
        z_movement = 0
        if direction == "forward":
            x_movement -= dt * self.playerMoveSpeed * sin(degToRad(self.h))
            y_movement += dt * self.playerMoveSpeed * cos(degToRad(self.h))
            # z_movement += dt * self.playerMoveSpeed * sin(degToRad(self.p))
        if direction == "backward":
            x_movement += dt * self.playerMoveSpeed * sin(degToRad(self.h))
            y_movement -= dt * self.playerMoveSpeed * cos(degToRad(self.h))
            # z_movement += dt * self.playerMoveSpeed * sin(degToRad(self.p))
        if direction == "right":
            x_movement += dt * self.playerMoveSpeed * cos(degToRad(self.h))
            y_movement += dt * self.playerMoveSpeed * sin(degToRad(self.h))
            # z_movement += dt * self.playerMoveSpeed * sin(degToRad(self.p))
        if direction == "left":
            x_movement -= dt * self.playerMoveSpeed * cos(degToRad(self.h))
            y_movement -= dt * self.playerMoveSpeed * sin(degToRad(self.h))
            # z_movement += dt * playerMoveSpeed * sin(degToRad(self.p))
        self.player.setPos(self.player.getX() + x_movement, self.player.getY() + y_movement,
                           self.player.getZ() + z_movement)

    def rotate_player(self, dx, dy):
        if self.can_move:
            self.h -= dx * 50
            self.p += dy * 50
            # self.h = np.clip(self.h, -90, 90)
            self.p = np.clip(self.p, -90, 90)

            camera.setHpr(self.h, self.p, 0)

    def jump(self):
        if self.grounded and not self.is_jumping:
            self.is_jumping = True
            self.delta_z = -.1

    def update_gravity(self, dt):
        if self.grounded:
            if self.delta_z > 0:
                self.is_jumping = False
                self.delta_z = 0
        else:
            if self.delta_z < self.max_acceleration:
                self.delta_z += self.acceleration * dt
        self.event_manager.sortEntries()
        entries = list(self.event_manager.entries)[1:]
        if entries:

            entry = min(entries, key=lambda a: abs(self.player.getZ() - a.getSurfacePoint(render).getZ()))

            z = entry.getSurfacePoint(render).getZ()
            # name = entry.getIntoNode().getName()
            # print(name)

            if self.player.getZ() - 1 > z:

                self.grounded = False
            else:

                self.grounded = True
        else:
            self.grounded = False

        self.player.setZ(self.player.getZ() - self.delta_z)

    def left_click(self):

        if base.mouseWatcherNode.hasMouse() and self.can_move:
            # get the mouse position
            mpos = base.mouseWatcherNode.getMouse()

            # set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(render)
            if list(self.pq.entries):
                # entry = min(list(self.pq.entries),
                #             key=lambda a: get_distance(a.getIntoNodePath().findNetTag('block').getPos(), camera.getPos()))
                # #entry = self.pq.entries[0]
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()

                if pickedObj.isEmpty():
                    return
                if not pickedObj.findNetTag('entity').isEmpty():
                    pickedObj = pickedObj.findNetTag('entity')
                    entity = self.world.get_entity(pickedObj.name)[0]
                    if entity is not None:
                        self.server_manager.hit_player(entity["name"])
                else:
                    pass
                    pickedObj = pickedObj.findNetTag('block')
                    # print(pickedObj.getPos())
                    # pickedObj.setColor(255, 0, 0, 255)
                    # pickedObj.remove_node()
                    if get_distance(pickedObj.getPos(), camera.getPos()) <= 5:
                        # block = self.world.removeBlock(pickedObj.getPos())
                        thread.start_new_thread(lambda: self.server_manager.pop_block(self.name, pickedObj.getPos()),
                                                "")

                        # self.server_manager.pop_block(pickedObj.getPos())

                        # self.world.player_removed_blocks.append(block)
                    # self.world.update_world()
                    # self.world.removeBlock(pickedObj.getPos())
            # if self.pq.getNumEntries() > 0:
            #
            #     self.pq.sortEntries()
            #     pickedObj = self.pq.getEntry(0).getIntoNodePath()
            #     node = self.pq.getEntry(0).getIntoNode()
            #     #x, y, z = self.pq.getEntry(0).getSurfaceNormal(render)
            #     print(r)

    def right_click(self):

        if base.mouseWatcherNode.hasMouse() and self.can_move:
            # get the mouse position
            mpos = base.mouseWatcherNode.getMouse()

            # set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(render)
            self.pq.sortEntries()
            if list(self.pq.entries):

                entry = min(list(self.pq.entries),
                            key=lambda a: get_distance(a.getSurfacePoint(render), camera.getPos()))
                self.pq.sortEntries()
                pickedObj = entry.getIntoNodePath().findNetTag('block')
                if not pickedObj.isEmpty():
                    normal = entry.getSurfaceNormal(render)
                    position = pickedObj.getPos() + normal

                    if get_distance(position, camera.getPos()) <= 5 and self.inventory:
                        # block = self.world.addBlock(position=position, block_type="stone")
                        # self.world.player_added_blocks.append(block)

                        thread.start_new_thread(lambda: self.server_manager.set_block(self.name, self.inventory[
                            self.current_inventory_item]["item_type"], position), "")
                        # self.server_manager.set_block(position)
                        # self.world.player_added_blocks.append(block)
                        # self.world.update_world()

    def swich_key(self, key, n):
        self.keys[key] = n
