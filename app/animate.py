class Animation:
    x = 0
    anim = None

    def __init__(self, animation):
        self.anim = animation

    def animate(self, speed, dt):
        self.x += speed * dt

    def get_animation(self):
        return self.anim(self.x)
