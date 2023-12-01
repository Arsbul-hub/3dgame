from direct.showbase.DirectObject import DirectObject
from panda3d.core import AudioSound


class SoundManager(DirectObject):
    sounds: dict
    volume = .5

    def prepare_sounds(self, base):

        self.sounds = {"gun": base.loader.loadSfx("./app/static/sounds/gun.ogg"),
                       "block_broke": base.loader.loadSfx("./app/static/sounds/block_broke.mp3"),
                       "walk": base.loader.loadSfx("./app/static/sounds/walk.mp3")
                       }

    def play(self, sound_name, volume=.5):
        if not self.sounds:
            return
        sound = self.sounds[sound_name]
        sound.setVolume(volume)
        if sound.status() == AudioSound.PLAYING:
            sound.stop()
        sound.play()

    def play_lasy(self, sound_name, volume=.5):
        if not self.sounds:
            return
        sound = self.sounds[sound_name]
        sound.setVolume(volume)
        if sound.status() != AudioSound.PLAYING:
            sound.play()


    def play_gun(self):
        self.play("gun", .2)

    def play_broke(self):
        self.play("block_broke")

    def play_walk(self):

        self.play_lasy("walk", .2)
