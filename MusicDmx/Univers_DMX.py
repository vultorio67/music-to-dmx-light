#define all the elements of the univers
import threading
import time
from typing import List, Callable, Optional

from MusicDmx.DmxSignalGenerator import DMXSignalGenerator
from MusicDmx.fixtures.DmxFixtures import DMXFixture, LyreSylvain, MyLight, CouleurDMX, DMXLightFixtures, LyreGroup
from Util import Config


class Univers_DMX:
    def __init__(self, controller):
        self.right_element : List[DMXFixture] = []
        self.left_element : List[DMXFixture] = []
        self.top_element : List[DMXFixture] = []
        self.bottom_element : List[DMXFixture] = []
        self.other_element : List[DMXFixture] = []

        self.mainController = controller

        self.cfg = self.mainController.config
        self.dmxSignalGenerator = self.mainController.dmxSignalGenerator

        #init directly from config
        self.addFromConfig()

        self._task_done = threading.Event()
        self._thread = None

    def addRightElement(self, add):
        self.right_element.append(add)
    def addLeftElement(self, add):
        self.left_element.append(add)
    def addTopElement(self, add):
        self.top_element.append(add)
    def addBottomElement(self, add):
        self.bottom_element.append(add)
    def addOtherElement(self, add):
        self.other_element.append(add)

    def addFromConfig(self):
        for ft in self.cfg.get_fixtures("right"):
            self.addRightElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("left"):
            self.addLeftElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("top"):
            self.addTopElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("bottom"):
            self.addBottomElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("other"):
            self.addOtherElement(self.constructFixturesElement(ft))


    #add here new element identification
    def constructFixturesElement(self, fixtures_config):

        fixture_type = fixtures_config.get('type')

        if fixture_type == "LyreSylvain":
            return LyreSylvain(fixtures_config['name'], fixtures_config['adresse'], self.dmxSignalGenerator)

        elif fixture_type == "MyLight":
            return MyLight(fixtures_config['name'], fixtures_config['adresse'], self.dmxSignalGenerator)

        else:
            raise ValueError(
                f"Type de fixture inconnu : {fixture_type} pour le projecteur '{fixtures_config.get('name', 'inconnu')}'")


    def getAllFixtures(self) -> DMXFixture:
        allFixtures: List[DMXFixture] = []
        for ft in self.right_element:
            allFixtures.append(ft)
        for ft in self.left_element:
            allFixtures.append(ft)
        for ft in self.top_element:
            allFixtures.append(ft)
        for ft in self.bottom_element:
            allFixtures.append(ft)
        for ft in self.other_element:
            allFixtures.append(ft)
        return allFixtures


    def getAllLightFixtures(self) -> DMXLightFixtures:
        allFixtures: List[DMXFixture] = []
        for ft in self.right_element:
            if isinstance(ft, DMXLightFixtures):
                allFixtures.append(ft)
        for ft in self.left_element:
            if isinstance(ft, DMXLightFixtures):
                allFixtures.append(ft)
        for ft in self.top_element:
            if isinstance(ft, DMXLightFixtures):
                allFixtures.append(ft)
        for ft in self.bottom_element:
            if isinstance(ft, DMXLightFixtures):
                allFixtures.append(ft)
        for ft in self.other_element:
            if isinstance(ft, DMXLightFixtures):
                allFixtures.append(ft)
        return allFixtures

    def enableAllLight(self, enable=True):
        for ft in self.getAllLightFixtures():
            if isinstance(ft, DMXLightFixtures):
                ft.enableLight(enable)


    def getRightFixtures(self):
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return fixtures

    def getLefttFixtures(self):
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return fixtures

    def getTopFixtures(self):
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return fixtures

    def getBottomFixtures(self):
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return fixtures

    def getOtherFixtures(self):
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return fixtures

    def setAllColor(self, color:CouleurDMX):
        for i in self.getAllFixtures():
            if isinstance(i,DMXLightFixtures):
                i.setColor(color)

    def setAllLyreColor(self, color:CouleurDMX):
        for i in self.getAllFixtures():
            if isinstance(i,LyreSylvain):
                i.setColor(color)

    def resetAllMasterSlave(self):
        for i in self.getAllFixtures():
            if isinstance(i,LyreSylvain):
                i.mirror_slave = []

    def getAllLyre(self) -> LyreGroup:
        lyres = [f for f in self.getAllFixtures() if isinstance(f, LyreSylvain)]  # ou LyreSylvain, etc.
        return LyreGroup(lyres)

    def getRightLyres(self):
        lyres = [f for f in self.right_element if isinstance(f, LyreSylvain)]
        return LyreGroup(lyres)

    def getLeftLyres(self):
        lyres = [f for f in self.left_element if isinstance(f, LyreSylvain)]
        return LyreGroup(lyres)

    def getTopLyres(self):
        lyres = [f for f in self.top_element if isinstance(f, LyreSylvain)]
        return LyreGroup(lyres)

    def getBottomLyres(self):
        lyres = [f for f in self.bottom_element if isinstance(f, LyreSylvain)]
        return LyreGroup(lyres)

    def getOtherLyres(self):
        lyres = [f for f in self.other_element if isinstance(f, LyreSylvain)]
        return LyreGroup(lyres)

    def getMyLight(self):
        for fixture in self.getAllFixtures():
            if isinstance(fixture, MyLight):
                return fixture

    def turnOffAllLight(self):
        for ft in self.getAllLightFixtures():
            if isinstance(ft, DMXLightFixtures):
                ft.turnOffAllLight()

    def strobAllLight(self, speed):
        for ft in self.getAllLightFixtures():
            if isinstance(ft, DMXLightFixtures):
                ft.setStroboscopeSpeed(speed)
