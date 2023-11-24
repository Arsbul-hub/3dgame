from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject

class SceneManager:
    scenes = {}
    def add(self, name, scene):
        self.scenes[name] = scene

    def load(self):

class Scene(DirectObject):
    objects = {}

    def clear(self):
        for name, obj in self.objects.items():
            obj.hide()
            self.objects.pop(name)

    def add(self, name, obj):
        self.objects[name] = obj


class MainScene(Scene):

    def __init__(self):
        super().__init__()
        self.player_name = ""
        myfont = loader.loadFont('arial.ttf')

        self.add("title", OnscreenText(text='Игра специально для Ивана Гагарина!', font=myfont, pos=(0, 0.5),
                                       scale=0.07))

        self.add("subtitle", OnscreenText(text='Ваш ник:', font=myfont, pos=(0, 0.2),
                                          scale=0.07))
        self.add("player_name", OnscreenText(text='', font=myfont, pos=(0, 0),
                                             scale=0.07))
        for s in "abcdefghijklmnopqrstuvwxyz":
            self.accept(s, self.set_name, [s])

        self.accept("backspace", self.clear_name)

    def set_name(self, sumb):
        self.player_name += sumb

        self.objects["player_name"].text = self.player_name

    def clear_name(self):
        if self.player_name:
            self.player_name = self.player_name[:-1]
        self.objects["player_name"].text = self.player_name
