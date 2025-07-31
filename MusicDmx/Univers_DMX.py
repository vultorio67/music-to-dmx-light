#define all the elements of the univers
import logging
import threading
import time
from typing import List, Callable, Optional

import Util
from MusicDmx.DmxSignalGenerator import DMXSignalGenerator
from MusicDmx.fixtures.DMXGroupes import DMXFixtureGroupe, DMXFixtureGroupe, getSpotLightList
from MusicDmx.fixtures.DmxFixtures import DMXFixture, LyreSylvain, MyLight, CouleurDMX, DMXLightFixtures, \
    DMXLightRGBFixtures, LyreWash, DMXMovingHeadFixture
from Util import Config


class Univers_DMX:
    def __init__(self, controller):
        self.right_element : List[DMXFixture] = []
        self.left_element : List[DMXFixture] = []
        self.top_element : List[DMXFixture] = []
        self.bottom_element : List[DMXFixture] = []
        self.other_element : List[DMXFixture] = []

        logging.info('[Univers_dmx] Initializing Univers_DMX')

        self.mainController = controller

        self.cfg = self.mainController.config
        self.dmxSignalGenerator = self.mainController.dmxSignalGenerator

        #init directly from config
        self.addFromConfig()

        self._task_done = threading.Event()
        self._thread = None

    def addRightElement(self, add):
        self.right_element.append(add)
        logging.info(f"[Univers_dmx] Adding on right: {add}")
    def addLeftElement(self, add):
        self.left_element.append(add)
        logging.info(f"[Univers_dmx] Adding on left: {add}")
    def addTopElement(self, add):
        self.top_element.append(add)
        logging.info(f"[Univers_dmx] Adding on top: {add}")
    def addBottomElement(self, add):
        self.bottom_element.append(add)
        logging.info(f"[Univers_dmx] Adding on bottom: {add}")
    def addOtherElement(self, add):
        self.other_element.append(add)
        logging.info(f"[Univers_dmx] Adding on other: {add}")


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

        elif fixture_type == "LyreWash":
            return LyreWash(fixtures_config['name'], fixtures_config['adresse'], self.dmxSignalGenerator)

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

        allFixtures: List[DMXLightFixtures] = []
        for ft in self.getAllFixtures():
            if isinstance(ft, DMXLightFixtures):
                allFixtures.append(ft)
        return DMXFixtureGroupe(allFixtures)

    def enableAllLight(self, enable=True):
        for ft in self.getAllLightFixtures().getFixturesList():
            if isinstance(ft, DMXLightFixtures):
                ft.enableLight(enable)

    def getRightFixtures(self) -> DMXFixture:
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return DMXFixtureGroupe(fixtures)

    def getLefttFixtures(self) -> DMXFixture:
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return DMXFixtureGroupe(fixtures)

    def getTopFixtures(self) -> DMXFixture:
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return DMXFixtureGroupe(fixtures)

    def getBottomFixtures(self) -> DMXFixture:
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return DMXFixtureGroupe(fixtures)

    def getOtherFixtures(self) -> DMXFixture:
        fixtures: List[DMXFixture] = []
        for ft in self.right_element:
            fixtures.append(ft)
        return DMXFixtureGroupe(fixtures)

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

    def getAllMovingHead(self) -> DMXMovingHeadFixture:
        lyres = [f for f in self.getAllFixtures() if isinstance(f, LyreSylvain)]  # ou LyreSylvain, etc.
        return DMXFixtureGroupe(lyres)

    ## For now we take LyreSylvain because I don't want to have the wash
    def getRightMovingHead(self) -> LyreSylvain:
        lyres = [f for f in self.right_element if isinstance(f, LyreSylvain)]
        return DMXFixtureGroupe(lyres)

    def getLeftMovingHead(self) -> LyreSylvain:
        lyres = [f for f in self.left_element if isinstance(f, LyreSylvain)]
        return DMXFixtureGroupe(lyres)

    def getTopMovingHead(self) -> LyreSylvain:
        lyres = [f for f in self.top_element if isinstance(f, LyreSylvain)]
        return DMXFixtureGroupe(lyres)

    def getBottomMovingHead(self) -> LyreSylvain:
        lyres = [f for f in self.bottom_element if isinstance(f, LyreSylvain)]
        return DMXFixtureGroupe(lyres)

    def getOtherMovingHead(self) -> LyreSylvain :
        lyres = [f for f in self.other_element if isinstance(f, LyreSylvain)]
        return DMXFixtureGroupe(lyres)
    

    #Lyrewash
    def getAllLyreWash(self) -> LyreWash:
        lyres = [f for f in self.getAllFixtures() if isinstance(f, LyreWash)]
        return DMXFixtureGroupe(lyres)

    def getRightLyreWash(self) -> LyreWash:
        lyres = [f for f in self.right_element if isinstance(f, LyreWash)]
        return DMXFixtureGroupe(lyres)

    def getLeftLyreWash(self) -> LyreWash:
        lyres = [f for f in self.left_element if isinstance(f, LyreWash)]
        return DMXFixtureGroupe(lyres)

    def getTopLyreWash(self) -> LyreWash:
        lyres = [f for f in self.top_element if isinstance(f, LyreWash)]
        return DMXFixtureGroupe(lyres)

    def getBottomLyreWash(self) -> LyreWash:
        lyres = [f for f in self.bottom_element if isinstance(f, LyreWash)]
        return DMXFixtureGroupe(lyres)

    def getOtherLyreWash(self) -> LyreWash:
        lyres = [f for f in self.other_element if isinstance(f, LyreWash)]
        return DMXFixtureGroupe(lyres)
    

    def getAllRGBLight(self) -> DMXLightRGBFixtures:
        RGBLight = [f for f in self.getAllFixtures() if isinstance(f, DMXLightRGBFixtures)]  # ou LyreSylvain, etc.
        return DMXFixtureGroupe(RGBLight)

    def getTopRGBLight(self) -> DMXLightRGBFixtures:
        RGBLight = [f for f in self.getTopFixtures().getFixturesList() if isinstance(f, DMXLightRGBFixtures)]
        return DMXFixtureGroupe(RGBLight)

    def getRightRGBLight(self) -> DMXLightRGBFixtures:
        RGBLight = [f for f in self.getRightFixtures().getFixturesList() if isinstance(f, DMXLightRGBFixtures)]
        return DMXFixtureGroupe(RGBLight)

    def getLeftRGBLight(self) -> DMXLightRGBFixtures:
        RGBLight = [f for f in self.getLefttFixtures().getFixturesList() if isinstance(f, DMXLightRGBFixtures)]
        return DMXFixtureGroupe(RGBLight)

    def getBottomRGBLight(self) -> DMXLightRGBFixtures:
        RGBLight = [f for f in self.getBottomFixtures().getFixturesList() if isinstance(f, DMXLightRGBFixtures)]
        return DMXFixtureGroupe(RGBLight)

    def getOtherRGBLight(self) -> DMXLightRGBFixtures:
        RGBLight = [f for f in self.getOtherFixtures().getFixturesList() if isinstance(f, DMXLightRGBFixtures)]
        return DMXFixtureGroupe(RGBLight)

    def getMyLight(self) -> MyLight:
        for fixture in self.getAllFixtures():
            if isinstance(fixture, MyLight):
                return fixture

    def turnOffAllLight(self):
        self.getAllLightFixtures().turnOffAllLight()

    def strobAllLight(self, speed):
        self.getAllLightFixtures().setStroboscopeSpeed(speed)

    def getAllSpotLight(self) -> DMXLightRGBFixtures:
        spotLight = []
        for fixture in self.getAllLightFixtures().getFixturesList():
            for spot in getSpotLightList():
                if isinstance(fixture, spot):
                    spotLight.append(fixture)
        return DMXFixtureGroupe(spotLight)

