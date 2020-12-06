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
        self.info = {}
        self.connect()
        logging.info(f"{self} created.")


    def __repr__(self):
        return f"Arduino on {self.port} (id={id(self)})"

    def connect(self):
        if self.arduino is None or not self.arduino.isOpen():
            try:
                self.arduino = serial.Serial(self.port, 9600, timeout = 1)
                #time.sleep(0.1)
            except serial.serialutil.SerialException:
                pass
            if self.arduino and self.arduino.isOpen():
                self.arduino.flushInput()
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
        '''Send la hauteur du seuil haut ou bas lié à la cellule
            index       :   index de la cellule
            haut_bas    :   'haut' ou 'bas' selon que l'on parle du seuil heut ou bas
            hauteur     :   hauteur (en pas)
        '''
        logging.debug(f"send_hauteur : cell n° {index}, seuil {haut_bas}, hauteur = {hauteur}")
        self.send_order("SHS", index, "B" if haut_bas == 'bas' else 'H', hauteur)
        time.sleep(0.5)

    def send_distance_pistolet(self, index, distance ):
        '''Envoie la distance entre le pristolet et les cellules
            index       :   index du pistolet
            distance     :   distance entre cellules et pistolet (en pas)
        '''
        logging.debug(f"send_distance_pistolet : P{index}, distance = {distance}")
        self.send_order("SDP", index, distance)
        time.sleep(0.5)

    def send_init(self):
        '''Initialise l'arduino (vide la memoire)
        '''
        logging.debug(f"Init arduino")
        self.send_order("INIT")
        time.sleep(1)


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

    def _read(self):
        '''Read the serial port
        '''
        lines = []
        if self.connect():
            try:
                while self.arduino.inWaiting()>0:
                    lines.append(self.arduino.readline())
                    #logging.debug(lines[-1])
                return lines
            except OSError:
                logging.error(f"Arduino on {self.port} not connected.")
                self.arduino.close()
        return []

    def ask_info(self):
        '''Send a INFO order to serial
        '''
        self.send_order("INFO")

    def get_info(self):
        '''Get info
        '''
        return self.info

    def read(self):
        '''Read the serial port, if INFO is detect update self.info
        '''
        for line in self._read():
            #logging.debug(line)
            if len(line)>4 and line[:4]==b'INFO':
                liste = line.split(b' ')
                if len(liste) > 2: #Au moins 'INFO', hauteur et 1 pistolet
                    info = {}
                    info['hauteur'] = int(liste[1])
                    for p in range(len(liste)-2):
                        info[p] = bool(int(liste[p+2]))
                    self.info = info
                else:
                    logging.debug(f"Arduino : Error on {line}")
            else:
                logging.debug(f"Arduino : {line}")
