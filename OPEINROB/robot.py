#!/usr/bin/env python
# -*- coding:utf-8 -*

'''
Un robot de peinture
piloté par ar raspberry pi
'''



class RobotPeint(objet):

    def __init__(self, detection_entree):
        '''Initialisation
        detection_avance        :   DetectionAvance object
        detection_entree        :   DetectionEntree object
        monte_baisse            :   MonteBaisse object
        '''
        self.detection_entree = detection_entree

    def run(self):
        '''Run forever
        '''
