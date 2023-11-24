from direct.showbase.DirectObject import DirectObject


class SceneManager(DirectObject):

    def __init__(self):
        super().__init__()
        self.scene_list = []



    def load_world(self):
        pass