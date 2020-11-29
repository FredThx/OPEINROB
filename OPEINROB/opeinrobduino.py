#!/usr/bin/env python
# -*- coding:utf-8 -*
import logging, serial, time
from bitarray import bitarray

class OPeinRobDuino():
    '''Un arduino sur lequel est connecté
        - commande pistolets de peinture
        - capteur monte&baisse
        - fin de course monte&baisse
        - capteur avance chaine

        Relié via serial
    '''
    def __init__(self, port):
        '''
            - port  :   serial port (ex '/dev/ttyACM0')
        '''
        self.port = port
        self.arduino = None
        self.connect()

    def connect(self):
        if self.arduino is None or not self.arduino.isOpen():
            self.arduino = serial.Serial(self.port, 9600, timeout = 1)
            time.sleep(0.1)
            if self.arduino.isOpen():
                logging.info(f"Arduino connected on {self.port}")
            else:
                logging.error(f"Arduino on {self.port} not connected.")

    def send_cells(self, cells_state):
        '''Send the state of the cells
            cells_state     :   a List
        '''
        logging.debug(f"send_cells : {cells_state}")
        self.send_order([0,0,0],0,cells_state)

    def send_hauteur(self, index, haut_bas, hauteur ):
        '''Send la hauteur de la cellule
            index       :   index de la cellule
            haut_bas    :   'haut' ou 'bas' selon que l'on parle du seuil heut ou bas
            hauteur     :   hauteur (en pas)
        '''
        logging.debug(f"send_hauteur : cell n° {index}, seuil {haut_bas}, hauteur = {hauteur}")
        seuil = haut_bas == 'haut'
        self.send_order([0,1,seuil],index,hauteur)

    def send_distance_pistolet(self, index, distance ):
        '''Send la hauteur de la cellule
            index       :   index du pistolet
            distance     :   distance entre cellules et pistolet (en pas)
        '''
        logging.debug(f"send_distance_pistolet : P{index}, distance = {distance}")
        self.send_order([1,1,0],index,distance)

    def send_order(self,a,b,d):
        '''Send to the arduino
            -a       :  order type :
                            [0,0,0] pour envoie cells
                            [0,1,0] : set hauteur cellules seuil bas
                            [0,1,1] : set hauteur cellules seuil haut
                            [1,1,0] : set distance pistolet]
            -b       :  index de la cellule ou pistolet
            -d       :  datas [d0,...]
            C'est à dire envoyer 2 bytes
            [0,a0,a1,a2,b0,b1,b2,d0][1,d1,d2,d3,d4,d5,d6,d7]
            (attention, il faut écrire le bitarray dans l'autre sens)
        '''
        a.reverse()
        b = bin(b)[2:]
        b = '0'*(3-len(b))+b
        b =  b[::-1]
        d.reverse()
        d = [0]*(8-len(d)) + d
        buf = bitarray(16)
        buf[15] = 0 # for the 1st byte
        buf[12:15] = bitarray(a)
        buf[9:12] = bitarray(b)
        buf[8] = d[-1] # 1ere cellule
        buf[7] = 1 # for the 2nd byte
        buf[:7] = bitarray(d[:-1])
        logging.debug(f"send_cells : {buf}")
        self.connect()
        self.arduino.write(buf.tobytes())

    def read(self):
        while self.arduino.inWaiting()>0:
            line = self.arduino.readline()
            #self.arduino.flushInput()
            logging.debug(f"Arduino : {line}")
