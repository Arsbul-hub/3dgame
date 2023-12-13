import asyncio
import json
import os
import random
import sys
# import threading

from math import *

try:
    os.chdir(sys._MEIPASS)  # картинка не загружается даже с add-data
except AttributeError:
    print("Запуск из исходника")

from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.ShowBase import ShowBase
# from direct.stdpy import thread

from panda3d.core import *

from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import Task
from panda3d.core import CollisionBox, CollisionNode, Vec3, CollisionSphere, CollisionHandlerPusher, loadPrcFileData, \
    CollisionTraverser, BitMask32, WindowProperties, CollisionCapsule
from requests import get
# from direct.stdpy import threading2, thread, threading

from app.scene_manager import SceneManager
from app.world import World
from app.player import Player

loadPrcFileData('', 'win-size 1224 768')
loadPrcFileData('', 'show-frame-rate-meter true')
loadPrcFileData('', 'threading-model App/Cull/Draw')
loadPrcFileData('', "sync-video true")

# from panda3d.core import Thread
# print(Thread.isThreadingSupported())
from app import server_manager, player, collision_manager, ServerManager, sound_manager
from direct.stdpy import threading, thread
# ALSO RIGHT:
from direct.stdpy import threading2
from direct.gui.OnscreenText import OnscreenText

# r = random.randint(0, 10000)
r = 130


# python3 -m pyinstaller --noconfirm --onedir --windowed --add-data "/home/arsbul/Рабочий стол/3dgame:3dgame/" --add-data "/home/arsbul/Рабочий стол/3dgame/arial.ttf:." --add-data "/home/arsbul/Рабочий стол/3dgame/config.json:."  "/home/arsbul/Рабочий стол/3dgame/main.py"

# print(r)
# name = "Arsbul"
# if len(sys.argv[1:]):
#     name = sys.argv[1]


def degToRad(degrees):
    return degrees * (pi / 180.0)


class MyApp(ShowBase):
    keys = {}
    lastMouseX = 0
    lastMouseY = 0
    camera_x = 0
    camera_y = 0
    player_name = ""
    game_started = False
    is_game_paused = False

    def __init__(self):
        ShowBase.__init__(self)
        self.player_name = ""
        base.cTrav = CollisionTraverser()
        self.scene_manager = SceneManager()
        sound_manager.prepare_sounds(self)
        self.main_font = loader.loadFont('app/static/fonts/arial.ttf')
        # scene = MainScene()
        self.load_main_menu()
        self.title = OnscreenText(text='3D Игра для Ивана Гагарина!', font=self.main_font, pos=(0, 0.5),
                                  scale=0.07)

        self.subtitle = OnscreenText(text='Ваш ник:', font=self.main_font, pos=(0, 0.2),
                                     scale=0.07)
        self.player_name_text = OnscreenText(text='', font=self.main_font, pos=(0, 0),
                                             scale=0.07)
        self.play_button = DirectButton(text="Играть", text0_font=self.main_font, text1_font=self.main_font,
                                        text2_font=self.main_font, pos=Vec3(0, -0.2), scale=.1,
                                        command=self.load_game)
        self.health_text = OnscreenText(text='', font=self.main_font, pos=(-1, 0.9),
                                        scale=0.07)

        self.unpause_button = DirectButton(text="Играть", text0_font=self.main_font, text1_font=self.main_font,
                                           text2_font=self.main_font, pos=Vec3(0, -0.2), scale=.1,
                                           command=self.unpause_game)
        self.unpause_button.hide()
        self.current_inventory_item = OnscreenImage(image="./app/static/images/textures/cobblestone.png",
                                                    pos=(0, 0, -0.6),
                                                    scale=0.1)
        self.current_inventory_item.setTransparency(TransparencyAttrib.MAlpha)
        self.current_inventory_item.hide()
        self.current_inventory_item_count = OnscreenText(text='', font=self.main_font,
                                                         pos=(0, -0.8),
                                                         scale=0.07)
        self.current_inventory_item_count.hide()

        self.crosshair = OnscreenImage(image="./app/static/images/icons/crosshair.png",
                                       pos=(0, 0, 0),
                                       scale=0.02)
        self.crosshair.setTransparency(TransparencyAttrib.MAlpha)
        self.crosshair.hide()
        self.connect_error_text = OnscreenText(text='Ошибка подключения к серверу!',
                                               fg=(.6, .1, .1, 1),
                                               font=self.main_font,
                                               pos=(0, -0.8),
                                               scale=0.07)

        self.connect_error_text.hide()
        # self.load_main_screen()
        # server_manager.connect_user(name)
        print(base.win.gsg.driver_vendor)
        print(base.win.gsg.driver_renderer)

        #
        # # player = Player(collision_manager)
        #
        # # self.server_manager.connect_user(self.player.name)
        # # self.load_world()
        # # self.load_player()
        # self.setupCamera()
        # self.taskMgr.add(self.update)
        # # self.taskMgr.add(self.world.update_world)
        # # self.load_player()
        # # threading.Thread(target=self.thread_update).start()
        # thread.start_new_thread(self.thread_update, "")
        # # threading2.Thread(target=self.world.update_world).start()
        # self.setupGUI()
        self.setup_light()
        self.setup_sky()
        self.setup_fog()
        render.setShaderAuto()

        self.accept("escape", self.pause_game)

    def setup_light(self):
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(1, 1, 1, 1))
        self.dlnp = render.attachNewNode(dlight)
        self.dlnp.setHpr(0, 240, 0)

        render.setLight(self.dlnp)
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = render.attachNewNode(alight)

        render.setLight(alnp)
    def setup_fog(self):
        color = (0.5, 0.8, 0.8)
        linfog = Fog("A linear-mode Fog node")
        linfog.setColor(*color)
        linfog.setLinearRange(5, 5)
        linfog.setLinearFallback(0, 0, 50)
        render.attachNewNode(linfog)
        render.setFog(linfog)
    def setup_sky(self):
        colour = (0.5, 0.8, 0.8)
        linfog = Fog("A linear-mode Fog node")
        linfog.setColor(*colour)
        linfog.setLinearRange(0, 320)
        linfog.setLinearFallback(0, 500, 550)
        fn = base.camera.attachNewNode(linfog)
        fn.setY(250)
        render.setFog(linfog)
        base.setBackgroundColor(*colour)

    def load_main_menu(self):

        for s in "abcdefghijklmnopqrstuvwxyz":
            self.accept(s, self.set_name, [s])

        self.accept("backspace", self.clear_name)

    def load_game(self):

        self.world = World(self.player_name)
        is_connected = server_manager.connect_user(self.player_name)
        if is_connected:
            self.player = Player(self.player_name, self.world, server_manager)
            # self.player.on_swich = self.update_gui
            self.setupCamera()

            # thread.start_new_thread(self.update_player, "")
            thread.start_new_thread(self.update_world, "")
            thread.start_new_thread(self.update_entities, "")
            thread.start_new_thread(self.update_player, "")
            self.taskMgr.add(self.update)
            self.taskMgr.add(self.update_gui)
            self.lockMouse()
            self.title.hide()
            self.subtitle.hide()
            self.player_name_text.hide()
            self.current_inventory_item.hide()
            self.current_inventory_item_count.show()
            self.play_button.hide()
            self.crosshair.show()
            self.connect_error_text.hide()
            self.game_started = True

        else:
            self.connect_error_text.show()

    def pause_game(self):
        self.player.disable_move()
        self.unpause_button.show()
        self.crosshair.hide()
        self.current_inventory_item.hide()
        self.current_inventory_item_count.hide()
        self.unlockMouse()
        self.is_game_paused = True

    def unpause_game(self):
        self.player.enable_move()
        self.unpause_button.hide()
        self.crosshair.show()
        self.current_inventory_item.show()
        self.current_inventory_item_count.show()
        self.lockMouse()
        self.is_game_paused = False

    def set_name(self, sumb):
        if not self.game_started:
            self.player_name += sumb

            self.player_name_text.text = self.player_name

    def clear_name(self):
        if not self.game_started:
            if self.player_name:
                self.player_name = self.player_name[:-1]
            self.player_name_text.text = self.player_name

    def update_world(self):
        while True:
            self.world.update_world()
            if not self.player.can_fall:
                self.player.can_fall = True

    def update_entities(self):
        while True:
            self.world.update_entities()

    def update_player(self):
        while True:
            self.player.update_pos()

    def setupCamera(self):
        self.disable_mouse()
        self.lens = PerspectiveLens()
        window_width, window_height = self.getSize()

        self.lens.setAspectRatio(window_width / window_height)
        self.lens.setFov(120)

        self.lens.setNear(0.01)

        # self.lens.setAspectRatio(2)
        self.cam.node().setLens(self.lens)

    def update(self, task):
        dt = globalClock.getDt()
        # self.camera.setPos(self.player.player.getX(), self.player.player.getY(), self.player.player.getZ() + 0.5)
        self.player.update_player(dt)

        self.moveCameraWithMouse(dt)
        # self.setupCamera()

        # print(self.player_name, self.world.current_entities)

        # self.camera.lookAt(self.pcn1)
        return task.cont

    async def update_gui(self, task):
        await task.pause(0)
        if self.player.inventory and not self.is_game_paused:
            inventory_item = self.player.inventory[self.player.current_inventory_item]

            self.current_inventory_item.setImage(f"./app/static/images/textures/{inventory_item['name']}.png")
            # self.current_inventory_item.setTransparency(TransparencyAttrib.MAlpha)
            self.current_inventory_item_count.setText(str(inventory_item["count"]))
        if self.world.player_entity:

            self.health_text.text = f"Здоровье: {int(self.world.player_entity['health'])}%"
        else:
            self.health_text.text = "Здоровье: 0"
        return task.cont

    def swich_key(self, key, n):
        self.keys[key] = n

    def moveCameraWithMouse(self, dt):
        mw = self.mouseWatcherNode
        if not self.is_game_paused:
            self.win.movePointer(0,
                                 int(self.win.getProperties().getXSize() / 2),
                                 int(self.win.getProperties().getYSize() / 2))
        if self.mouseWatcherNode.hasMouse():
            x, y = mw.getMouseX(), mw.getMouseY()

            self.player.rotate_player(x * 3, y * 3)
            # self.lastMouseX, self.lastMouseY = x, y

    def lockMouse(self):
        self.cameraSwingActivated = False
        properties = WindowProperties()
        properties.setCursorHidden(True)

        # properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

    def unlockMouse(self):
        self.cameraSwingActivated = True
        properties = WindowProperties()
        properties.setCursorHidden(False)

        # properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)


app = MyApp()
app.run()
