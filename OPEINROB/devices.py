#!/usr/bin/env python
# -*- coding:utf-8 -*



class Device(object):
    '''Super class pour tous les objets Device
    '''
    pass#On verra si util!.....

class DetectionAvance(Device):
    ''' Une cellule qui detecte l'avance de la chaine
    '''
    def __init__(self, pin):
        self.cellule = Cellule(pin)

class DetectionEntree(Device):
    '''Plusieurs cellules qui detectent les pièces à l'entrée du robot
    '''
    def __init__(self, pins = [], hauteurs = []):
        assert len(pins)==len(hauteurs),"len(pins) <> len(hauteurs) !"
        self.cells = []
        for i in range(len(pins)):
            self.cells.append(CelluleEntree(pins[i],hauteurs[i]))

class Cellule(Device):
    '''Une cellule
    '''
    def __init__(self, pin):
        self.pin = pin

class CelluleEntree(Cellule):
    '''une cellule d'entree
    '''
    def __init__(self, pin, hauteur):
        self.hauteur = hauteur
        super().__init__(self, pin)

class MonteBaisse(Device):
    '''Un monte et baisse (detecté par 1 roue codeuse et un fin de course)
    '''
    def __init__(self, pin_roue_codeuse, pin_fin_de_course):
        self.roue_codeuse = Cellule(pin_roue_codeuse)
        self.fin_de_course = Cellule(pin_fin_de_course)
