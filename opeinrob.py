#!/usr/bin/env python
# -*- coding:utf-8 -*


from FUTIL.my_logging import *
from OPEINROB.cellules import *
from OPEINROB.robot import *
from OPEINROB.opeinrobduino import *

my_logging(console_level = DEBUG, logfile_level = DEBUG, details = True, name_logfile = None)

robduino = OPeinRobDuino(port = "/dev/ttyACM0")
cellules = DetectionEntree(pins=[5,6,13,19,26],hauteurs=[42,42,42,42,42])
rob = RobotPeint(detection_entree = cellules, robduino = robduino)

rob.run()
