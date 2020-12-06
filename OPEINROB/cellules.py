#!/usr/bin/env python
# -*- coding:utf-8 -*

import RPi.GPIO as GPIO
import logging

class DetectionEntree():
    '''Plusieurs cellules qui detectent les pièces à l'entrée du robot
    '''
    def __init__(self, pins = [], seuils = None, pull = 'up'):
        '''
            -   pins    :   E/S for cells ex : [5,6,8]
            -   seuils  :   ex : [[20,50],[40,60],[50,60]]
        '''
        GPIO.setmode(GPIO.BCM)
        assert len(pins)<=8,"Trop de cellules. 8 maxi."
        assert seuils is None or len(pins)==len(seuils),"len(pins) <> len(seuils) !"
        self.cells = []
        if seuils is None:
            seuils = [[0,255]]*len(pins)
        for i in range(len(pins)):
            self.cells.append(CelluleEntree(pins[i],seuils[i][0],seuils[i][1], pull=pull))

    def read(self):
        '''Renvoie la liste des états des cellules
        '''
        return [cell.read() for cell in self.cells]

    def update_robduino(self, robduino):
        '''Update the robduino with seuil haut et bas
        '''
        for index, cell in enumerate(self.cells):
            cell.update_robduino(robduino, index)

class CelluleEntree():
    '''une cellule d'entree
    '''
    def __init__(self, pin, seuil_bas, seuil_haut, pull = 'up'):
        self.seuil_bas = seuil_bas
        self.seuil_haut = seuil_haut
        self.pin = pin
        self.pull = pull
        GPIO.setup(self.pin, GPIO.IN)

    def update_robduino(self, robduino, index):
        '''Update the robduino with seuil haut et bas
        '''
        robduino.send_hauteur(index, 'bas', self.seuil_bas)
        robduino.send_hauteur(index, 'haut', self.seuil_haut)

    def read(self):
        '''renvoie l'état de la cellule
        '''
        if self.pull == 'up':
            return self.gpio_not(GPIO.input(self.pin))
        else:
            return GPIO.input(self.pin)

    @staticmethod
    def gpio_not(val):
        if val == GPIO.LOW:
            return GPIO.HIGH
        else:
            return GPIO.LOW
