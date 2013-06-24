# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Application layer group data management

Implements
==========

 - B{L_DataService}
 - B{L_DSValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import threading

from pknyx.common.exception import PKNyXValueError
from pknyx.common.loggingServices import Logger
from pknyx.core.priorityQueue import PriorityQueue
from pknyx.core.layer3.n_groupDataListener import N_GroupDataListener
from pknyx.core.transceiver.transceiverLSAP import TransceiverLSAP
from pknyx.core.transceiver.transmission import Transmission
from pknyx.core.transceiver.tFrame import TFrame


class L_DSValueError(PKNyXValueError):
    """
    """


class L_DataService(threading.Thread, TransceiverLSAP):
    """ L_DataService class

    @ivar _ldl: link data listener
    @type _ldl: L{L_DataListener<pknyx.core.layer2.l_dataListener>}

    @ivar _inQueue: input queue
    @type _inQueue: L{PriorityQueue}

    @ivar _outQueue: output queue
    @type _outQueue: L{PriorityQueue}

    @ivar _running: True if thread is running
    @type _running: bool
    """
    def __init__(self, priorityDistribution):
        """

        @param priorityDistribution:
        @type priorityDistribution:

        raise L_DSValueError:
        """
        super(L_DataService, self).__init__(name="KNX Stack LinkLayer")

        self._ldl = None

        self._inQueue  = PriorityQueue(4, priorityDistribution)
        self._outQueue = PriorityQueue(4, priorityDistribution)

        self._running = False

        self.setDaemon(True)
        #self.start()

    def getOutFrame(self):
        """ Get output frame

        Blocks until there is a transmission pending in outQueue, then returns this transmission

        @return: pending transmission in outQueue
        @rtype: L{Transmission}
        """
        transmission = None

        # test outQueue for frames to transmit, else go sleeping
        self._outQueue.acquire()
        try:
            transmission = self._outQueue.remove()
            while transmission is None:
                self._outQueue.wait()
                transmission = self._outQueue.remove()
        finally:
            self._outQueue.release()

        return transmission

    def putInFrame(self, lPDU):
        """ Set input frame

        @param lPDU: Link Pxxx Data Unit
        @type: bytearray
        """

        # test Control Field (CF) - not necessary cause should be done by the transceiver or BCU
        # if (lPDU[TFrame.CF_BYTE] & TFrame.CF_MASK) != TFrame.CF_L_DATA:
        #     return

        # length of lPDU and length transmitted with lPDU must be equal
        length = (lPDU[TFrame.LEN_BYTE] & TFrame.LEN_MASK) >> TFrame.LEN_BITPOS
        if (lPDU[TFrame.LTP_BYTE] & TFrame.LTP_MASK) == TFrame.LTP_TABLE:
            length = TFrame.lenCode2Len(length)

        length += TFrame.MIN_LENGTH
        if length != len(lPDU):
            return

        # get priority from lPDU (move test in Priority object)
        if (lPDU[TFrame.PR_BYTE] & TFrame.PR_MASK) == TFrame.PR_SYSTEM:
            priority = Priority('system')
        elif (lPDU[TFrame.PR_BYTE] & TFrame.PR_MASK) == TFrame.PR_ALARM:
            priority = Priority('alarm')
        elif (lPDU[TFrame.PR_BYTE] & TFrame.PR_MASK) == TFrame.PR_HIGH:
            priority = Priority('high')
        elif (lPDU[TFrame.PR_BYTE] & TFrame.PR_MASK) == TFrame.PR_LOW:
            priority = Priority('low')
        else:
            priority = Priority('low')

        # add to inQueue and notify inQueue handler
        lPDU[TFrame.PR_BYTE] = priority  # memorize priority
        self._inQueue.acquire()
        try:
            self._inQueue.add(lPDU, priority)
            self._inQueue.notify()
        finally:
            self._inQueue.release()

    def setListener(self, lgdl):
        """

        @param ngdl: listener to use to transmit data
        @type ngdl: L{L_GroupDataListener<pknyx.core.layer2.l_groupDataListener>}
        """
        self._ldl = lgdl

    def dataReq(self, src, dest, isGAD, priority, lSDU):
        """
        """
        Logger().debug("N_GroupDataService.groupDataReq(): src=%s, dest=%s, isGAD=%S, priority=%s, lSDU=%s" % \
                       (src, dest, isGAD, priority, repr(lSDU)))

        if gad.isNull():
            raise N_GDSValueError("GAD is null")

        length = len(lSDU) - TFrame.MIN_LENGTH

        lSDU[TFrame.LTP_BYTE] = TFrame.LTP_TABLE if length > 15 else TFrame.LTP_BYTES
        lSDU[TFrame.PR_BYTE] |= TFrame.PR_CODE[pr]

        lSDU[TFrame.SAH_BYTE] = (src >> 8) & 0xff
        lSDU[TFrame.SAL_BYTE] = src & 0xff
        lSDU[TFrame.DAH_BYTE] = (dest >> 8) & 0xff
        lSDU[TFrame.DAL_BYTE] = dest & 0xff

        lSDU[TFrame.DAF_BYTE] |= TFrame.DAF_GAD if isGAD else TFrame.DAF_IA
        lSDU[TFrame.LEN_BYTE] |= (TFrame.len2LenCode(length) if length > 15 else length) << TFrame.LEN_BITPOS

        waitL2Con = True
        transmission = Transmission(lSDU, waitL2Con)
        transmission.acquire()
        try:
            self._outQueue.acquire()
            try:
                self._outQueue.add(transmission, priority)
                self._outQueue.notifyAll()
            finally:
                self._outQueue.release()

            while transmission.waitConfirm:
                transmission.wait()
        finally:
            transmission.release()

        return transmission.result

    def run(self):
        """ inQueue handler main loop
        """
        Logger().info("Start")

        self._running = True
        while self._running:
            try:

                # test inQueue for frames to handle, else go sleeping
                self._inQueue.acquire()
                try:
                    lPDU = self._inQueue.remove()
                    while lPDU == None:
                        self._inQueue.wait()
                        lPDU = self._inQueue.remove()
                finally:
                    self._inQueue.release()

                #handle frame
                src = ((lPDU[TFrame.SAH_BYTE] & 0xff) << 8) + (lPDU[TFrame.SAL_BYTE] & 0xff)
                dest = ((lPDU[TFrame.DAH_BYTE] & 0xff) << 8) + (lPDU[TFrame.DAL_BYTE] & 0xff)
                isGA = (lPDU[TFrame.DAF_BYTE] & TFrame.DAF_MASK) == TFrame.DAF_GAD
                priority = lPDU[TFrame.PR_BYTE]
                if self._ldl:
                    self.lgdl.dataInd(src, dest, isGA, priority, lPDU)

                print "alive"

            except:
                Logger().exception("L_DataService.run()", debug=True)

        Logger().info("Stop")

    def stop(self):
        """ stop thread
        """
        Logger().info("Stopping L_DataService")

        self._running = False

    def isRunning(self):
        """ test if thread is running

        @return: True if running, False otherwise
        @rtype: bool
        """
        return self._running


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class L_GDSTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
