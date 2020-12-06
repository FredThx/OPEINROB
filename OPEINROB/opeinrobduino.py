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

    def __repr__(self):
        return f"Arduino on {self.port}"

    def connect(self):
        if self.arduino is None or not self.arduino.isOpen():
            try:
                self.arduino = serial.Serial(self.port, 9600, timeout = 1)
                time.sleep(0.1)
            except serial.serialutil.SerialException:
                pass
            if self.arduino and self.arduino.isOpen():
                logging.info(f"Arduino connected on {self.port}")
                return True
            else:
                logging.error(f"Arduino on {self.port} not connected.")
                return False
        else:
            return True

    def send_cells(self, cells_state):
        '''Send the state of the cells
            cells_state     :   a List
        '''
        #logging.debug(f"send_cells : {cells_state}")
        #self.send_order([0,0,0],0,cells_state)
        self.send_order("SC",self.list_to_int(cells_state))

    def send_hauteur(self, index, haut_bas, hauteur ):
        '''Send la hauteur de la cellule
            index       :   index de la cellule
            haut_bas    :   'haut' ou 'bas' selon que l'on parle du seuil heut ou bas
            hauteur     :   hauteur (en pas)
        '''
        logging.debug(f"send_hauteur : cell n° {index}, seuil {haut_bas}, hauteur = {hauteur}")
        self.send_order("SHC", index, "B" if haut_bas == 'bas' else 'H', hauteur)

    def send_distance_pistolet(self, index, distance ):
        '''Send la hauteur de la cellule
            index       :   index du pistolet
            distance     :   distance entre cellules et pistolet (en pas)
        '''
        logging.debug(f"send_distance_pistolet : P{index}, distance = {distance}")
        self.send_order("SDP", index, distance)

    def send_init(self):
        '''Initialise l'arduino (vide la memoire)
        '''
        logging.debug(f"Init arduino")
        self.send_order("INIT")


    def send_order(self,order, *args):
        '''Send order to the arduino
            "ORDER ARG1 ARG2 ...."
        '''
        buf = order
        for arg in args:
            buf += " " + str(arg)
        buf += "\n"
        if self.connect():
            try:
                self.arduino.write(buf.encode('ascii'))
            except serial.SerialException:
                logging.error(f"Arduino on {self.port} not connected.")
        #logging.debug(f"Send {buf} on {self.arduino}")

    @staticmethod
    def list_to_int(l):
        '''get a list of digits (0 | 1)
            return a int
        '''
        result = 0
        for digit in l:
            result = (result << 1) | digit
        return result

    def read(self):
        if self.connect():
            try:
                while self.arduino.inWaiting()>0:
                    line = self.arduino.readline()
                    #self.arduino.flushInput()
                    logging.debug(f"Arduino : {line}")
            except OSError:
                logging.error(f"Arduino on {self.port} not connected.")
                self.arduino.close()
