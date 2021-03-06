# -*- coding: utf-8 -*-

import os
from pprint import pprint

from pyknyx.api import Device, FunctionalBlock, notify, DP, GO, FB, LNK
from pyknyx.core.ets import ETS
from pyknyx.tools.deviceRunner import *
import unittest

# Mute logger
from pyknyx.services.logger import logging
logger = logging.getLogger(__name__)
logging.getLogger("pyknyx").setLevel(logging.ERROR)
logger.setLevel(logging.ERROR)


# A toggle button
class ToggleFB(FunctionalBlock):

    # Datapoints (= Group Objects) definition
    change = DP(dptId="1.001", default="Off", access="output")
    DP_02 = dict(name="status", dptId="1.001", default="Off", access="input")
    GO_01 = GO(dp=change, flags="CT", priority="low")
    GO_02 = dict(dp="status", flags="CWUI", priority="low")
    DESC = "ToggleFB"

class ActorFB(FunctionalBlock):
    change = DP(dptId="1.001", default="Off", access="input")
    status = DP(dptId="1.001", default="Off", access="output", flags="CRT")
    GO_01 = dict(dp=change, flags="CW", priority="low")
    # GO_02 = GO(dp="status", flags="CRT", priority="low")
    DESC = "ActorFB"

    _current = None

    @notify.datapoint(dp="change", condition="change")
    def stateChanged(self, event):
        if event['newValue'] == "On":
            self.on = True
        else:
            self.on = False

    @property
    def on(self):
        return self.dp["status"].value == "On"
    @on.setter
    def on(self, value):
        self._current = value
        if value:
            self.dp["status"].value = "On"
        else:
            self.dp["status"].value = "Off"


class Toggle(Device):
    toggle_fb = FB(ToggleFB, desc="binary input")

    LNK_01 = LNK(toggle_fb.change, gad="1/1/1")
    LNK_02 = dict(fb="toggle_fb", dp="status", gad="1/2/1")

    def set(self, value):
        self.fb["toggle_fb"].dp["change"].value = "On" if value else "Off"
    @property
    def status(self):
        return self.fb["toggle_fb"].dp["status"].value == "On"

class Actor(Device):
    actor_fb = FB(ActorFB, desc="binary output")

class SwitchTestCase(unittest.TestCase):

    def setUp(self):
        self.ets = None
        self.ets2 = None

    def tearDown(self):
        if self.ets is not None:
            self.ets.stop()
        if self.ets2 is not None:
            self.ets2.stop()

    def test_multicast(self):
        self.ets = ETS("1.2.0", transParams=dict(mcastAddr="224.55.36.71", mcastPort=os.getpid()))
        self.ets2 = ETS("1.2.0", transParams=dict(mcastAddr="224.55.36.71", mcastPort=os.getpid()))
        self._do_test()

    def test_switch(self):
        self.ets = ETS("1.2.0", transCls=None)
        self.ets2 = self.ets
        self._do_test()

    def _do_test(self):
        self.actor = Actor(self.ets, "1.2.3",
            links=(LNK(Actor.actor_fb.change, "1/1/1"),
                   LNK(Actor.actor_fb.status, "1/2/1")))
        self.toggle = Toggle(self.ets2, "1.2.4")
        self.ets.start()
        if self.ets2 is not self.ets:
            self.ets2.start()
        afb = self.actor.fb["actor_fb"]
        assert afb._current is None
        time.sleep(0.5)
        logger.debug("Set TRUE")
        self.toggle.set(True)
        time.sleep(0.5)
        assert afb._current is True
        assert self.toggle.status
        logger.debug("Set FALSE")
        self.toggle.set(False)
        time.sleep(0.5)
        assert afb._current is False
        assert not self.toggle.status

