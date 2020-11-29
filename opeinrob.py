#!/usr/bin/env python
# -*- coding:utf-8 -*



from OPEINROB import *

cellules = DetectionEntree(pins=[21,22,23,24,25],hauteurs=[])
rob = RobotPeint(detection_entree = cellules)

rob.run()
