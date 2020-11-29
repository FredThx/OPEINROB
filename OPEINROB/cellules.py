#!/usr/bin/env python
# -*- coding:utf-8 -*

import RPi.GPIO as GPIO
import logging

class DetectionEntree():
    '''Plusieurs cellules qui detectent les pièces à l'entrée du robot
    '''
    def __init__(self, pins = [], hauteurs = [], pull = 'up'):
        GPIO.setmode(GPIO.BCM)
        assert len(pins)<=8,"Trop de cellules. 8 maxi."
        assert len(pins)==len(hauteurs),"len(pins) <> len(hauteurs) !"
        self.cells = []
        for i in range(len(pins)):
            self.cells.append(CelluleEntree(pins[i],hauteurs[i], pull=pull))

    def read(self):
        '''Renvoie la liste des états des cellules
        '''
        return [cell.read() for cell in self.cells]

class CelluleEntree():
    '''une cellule d'entree
    '''
    def __init__(self, pin, hauteur, pull = 'up'):
        self.hauteur = hauteur
        self.pin = pin
        self.pull = pull
        GPIO.setup(self.pin, GPIO.IN)

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
