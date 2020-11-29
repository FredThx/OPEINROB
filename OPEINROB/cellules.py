#!/usr/bin/env python
# -*- coding:utf-8 -*

import RPi.GPIO as GPIO
import logging

class DetectionEntree():
    '''Plusieurs cellules qui detectent les pièces à l'entrée du robot
    '''
    def __init__(self, pins = [], hauteurs = []):
        GPIO.setmode(GPIO.BCM)
        assert len(pins)<=8,"Trop de cellules. 8 maxi."
        assert len(pins)==len(hauteurs),"len(pins) <> len(hauteurs) !"
        self.cells = []
        for i in range(len(pins)):
            self.cells.append(CelluleEntree(pins[i],hauteurs[i]))
    def read(self):
        '''Renvoie la liste des états des cellules
        '''
        return [cell.read() for cell in self.cells]

class CelluleEntree():
    '''une cellule d'entree
    '''
    def __init__(self, pin, hauteur):
        self.hauteur = hauteur
        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN)

    def read(self):
        '''renvoie l'état de la cellule
        '''
        return GPIO.input(self.pin)
