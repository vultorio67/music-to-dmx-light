from MusicDmx import DmxController


class Scene:
    def __init__(self, dmxController: DmxController):
        self.dmxController = dmxController

    def activate(self):
        pass  # Override dans les sous-classes


class BeamIntro(Scene):
    def activate(self):
        self.controller.move_lyre('left', pan=45, tilt=30)
        self.controller.set_color('left', 'blue')
        self.controller.set_dimmer('left', 255)