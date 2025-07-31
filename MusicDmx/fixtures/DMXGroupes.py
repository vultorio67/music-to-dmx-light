#####les groupes #########
import logging

from MusicDmx.fixtures.DmxFixtures import DMXLightFixtures, DMXMovingHeadFixture, DMXLightRGBFixtures, MyLight, LyreWash


class DMXFixtureGroupe:
    def __init__(self, fixtures):
        self.fixtures = fixtures

    def __str__(self):
        lines = [f"{self.__class__.__name__} with {len(self.fixtures)} fixture(s):"]
        for fixture in self.fixtures:
            lines.append(f"  - {fixture.name} (adresse {fixture.start_address + 1})")
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, attr):
        def group_method(*args, **kwargs):
            for fixture in self.fixtures:
                method = getattr(fixture, attr, None)
                if callable(method):
                    method(*args, **kwargs)
                else:
                    logging.error(f"[WARN] {fixture.name} n’a pas la méthode {attr}")
        return group_method

    def getFixturesList(self):
        listOfFixtures = []
        for fixture in self.fixtures:
            listOfFixtures.append(fixture)
        return listOfFixtures

def getSpotLightList():
    return [MyLight, LyreWash]

"""class DMXMovingHeadGroupe:
    def __init__(self, fixtures):
        self.fixtures = fixtures

    def __getattr__(self, attr):
        def group_method(*args, **kwargs):
            for fixture in self.fixtures:
                method = getattr(fixture, attr, None)
                if callable(method):
                    method(*args, **kwargs)
                else:
                    logging.error(f"[WARN] {fixture.name} n’a pas la méthode {attr}")
        return group_method

    def setPos(self, pan, tilt):
        return self.__getattr__("setPos")(pan, tilt)

    def goToHomePosition(self):
        return self.__getattr__("goToHomePosition")()

    def move_to(self, pan, tilt, duration=1.0, steps=40):
        return self.__getattr__("move_to")(pan, tilt, duration=duration, steps=steps)

    def move_to_arc(self, pan, tilt, duration=1.0, radius=1, steps=40):
        return self.__getattr__("move_to_arc")(pan, tilt, duration=duration, radius=radius, steps=steps)

    def centerCircle(self, center_tilt, radius, duration=2.0, loops=1, steps=100):
        return self.__getattr__("centerCircle")(center_tilt, radius, duration, loops, steps)

    def ellipse(self, center_pan, center_tilt, radius_pan, radius_tilt, duration=2.0, loops=1, steps=100):
        return self.__getattr__("ellipse")(center_pan, center_tilt, radius_pan, radius_tilt, duration, loops, steps)

    def figure_8(self, center_pan, center_tilt, radius_pan, radius_tilt, duration=4.0, loops=1, steps=100):
        return self.__getattr__("figure_8")(center_pan, center_tilt, radius_pan, radius_tilt, duration, loops, steps)

    def diagonal_scan(self, pan_min, pan_max, tilt_min, tilt_max, duration=3.0, steps=50, loops=1):
        return self.__getattr__("diagonal_scan")(pan_min, pan_max, tilt_min, tilt_max, duration, steps, loops)

    def wave_horizontal(self, pan_min, pan_max, center_tilt, amplitude, duration=3.0, steps=100):
        return self.__getattr__("wave_horizontal")(pan_min, pan_max, center_tilt, amplitude, duration, steps)

    def zigzag(self, pan_min, pan_max, tilt_min, tilt_max, steps=10, duration=2.0, loops=1):
        return self.__getattr__("zigzag")(pan_min, pan_max, tilt_min, tilt_max, steps, duration, loops)

    def move_to_variable_speed(self, pan_target, tilt_target, duration=2.0, steps=40, easing_function=None):
        return self.__getattr__("move_to_variable_speed")(pan_target, tilt_target, duration, steps, easing_function)


class RGBLightGroupe():
    def __init__(self, lights):
        self.lights = lights

    # comme la méhode existe pas on l'applique à l'ensemble des lyres du groupe
    def __getattr__(self, attr):
        def group_method(*args, **kwargs):
            for fixture in self.fixtures:
                method = getattr(fixture, attr, None)
                if callable(method):
                    method(*args, **kwargs)
                else:
                    logging.error(f"[WARN] {fixture.name} n’a pas la méthode {attr}")
        return group_method

    def setColor(self, color):
        return self.__getattr__("setColor")(color)

    def enableLight(self, isEnabled):
        return self.__getattr__("enableLight")(isEnabled)

    def setStroboscopeSpeed(self, speed: int):
        return self.__getattr__("setStroboscopeSpeed")(speed)

    def turnOffAllLight(self):
        return self.__getattr__("turnOffAllLight")()

    def enableAutoMode(self, value):
        return self.__getattr__("enableAutoMode")(value)

    def set_param(self, param, value):
        return self.__getattr__("set_param")(param, value)
"""
