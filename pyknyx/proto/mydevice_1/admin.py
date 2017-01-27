#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Python KNX framework.

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

Device (process) management.

Implements
==========

Documentation
=============

This script handles the $PKNYX_DEVICE_PATH env. var for this device and calls pyknyx-admin.py main() function.

Usage
=====

See pyknyx-admin.py tools.

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

import os
import os.path
import sys


def main():
    os.environ.setdefault("PKNYX_DEVICE_PATH", os.path.join(os.path.dirname(__file__), "mydevice_1"))

    from pyknyx.services.adminUtility import AdminUtility

    AdminUtility().execute()


if __name__ == "__main__":
    main()
