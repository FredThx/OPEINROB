#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Un robot de peinture
piloté par ar raspberry pi
'''
import logging
import time
import threading



from OPEINROB.cellules import *

class RobotPeint():

    def __init__(self, detection_entree, robduino):
        '''Initialisation
            - detection_entree      :   DetectionEntree object (cellules)
            - robduino              :   OPeinRobDuino object (arduino avec OPEINROBDUINO.ino)
        '''
        self.detection_entree = detection_entree
        self.robduino = robduino
        self.p_send_cells = threading.Thread(target = self.send_cells, daemon = True)
        self.p_read_robduino = threading.Thread(target = self.read_robduino, daemon = True)
        self.p_get_info = threading.Thread(target = self.get_info, daemon = True)
        self.p_read_robduino.start()
        time.sleep(0.5)
        self.update_robduino()

    def update_robduino(self):
        self.detection_entree.update_robduino(self.robduino)

    def run(self):
        '''Run forever
        '''
        self.p_send_cells.start()
        self.p_get_info.start() #Pas utilisé encore
        try:
            while True:
                time.sleep(1)
        except  KeyboardInterrupt:
            pass

    def send_cells(self):
        ''' Process qui Envoie l'état des cellules à l'arduino
            forever
        '''
        while True:
            self.robduino.send_cells(self.detection_entree.read())
            time.sleep(1)

    def read_robduino(self):
        '''process qui va lire le serial port on robduino
            forever
        '''
        while True:
            self.robduino.read()


    def get_info(self):
        '''Process qui va envoyer la demande de INFO
        forever
        '''
        while True:
            self.robduino.ask_info()
            time.sleep(0.1) # 0.01 ne fonctionne pas 0.05 ok
            logging.debug(self.robduino.get_info())
