# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{PyKNyX} (U{https://github.com/knxd/pyknyx}) is Copyright:
  - © 2016-2017 Matthias Urlichs
  - PyKNyX is a fork of pKNyX
   - © 2013-2015 Frédéric Mantegazza

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

cEMI frame management

Implements
==========

 - B{CEMI}

Documentation
=============


Usage
=====

>>> from cemi import CEMI
>>> f = CEMI()

@author: Frédéric Mantegazza
@author: Bernhard Erb
@author: B. Malinowsky
@copyright: (C) 2013-2015 Frédéric Mantegazza
@copyright: (C) 2005 B. Erb
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""


from pyknyx.common.exception import PyKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)


class CEMIValueError(PyKNyXValueError):
    """
    """


class CEMI(object):
    """ cEMI handling

    @ivar payload:
    @type payload: bytearray
    """
    def __init__(self):  #, payload=None):
        """ Create a new cEMI object

        #@param payload:
        #@type payload: bytearray
        """
        super(CEMI, self).__init__()

        #self._payload = payload  # TODO: check validity

    def copy(self):
        raise NotImplemented

    #@property
    #def payload(self):
        #return self._payload

    @property
    def messageCode(self):
        raise NotImplemented

    @property
    def length(self):
        raise NotImplemented

    #@property
    #def byteArray(self):
        #raise NotImplemented

