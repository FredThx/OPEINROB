#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Un robot de peinture
piloté par ar raspberry pi
'''
import logging
import time
from OPEINROB.cellules import *

class RobotPeint():

    def __init__(self, detection_entree, robduino):
        '''Initialisation
        detection_avance        :   DetectionAvance object
        detection_entree        :   DetectionEntree object
        monte_baisse            :   MonteBaisse object
        '''
        self.detection_entree = detection_entree
        self.robduino = robduino
        self.update_robduino()

    def update_robduino(self):
        self.detection_entree.update_robduino(self.robduino)

    def run(self):
        '''Run forever
        '''
        try:
            while True:
                #logging.debug(f"Etat des cellules : {self.detection_entree.read()}")
                self.robduino.send_cells(self.detection_entree.read())
                self.robduino.read()
                time.sleep(0.1)
        except  KeyboardInterrupt:
            pass
