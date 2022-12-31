#!/usr/bin/env python3
################################################################################
#   Title: Serial Thread
# Project: VTGS/Telescope/Others
# Version: 1.0.0
#    Date: Nov, 2022
#  Author: Zach Leffke, KJ4QLP
# Comments:
#   -Thread for interacting with serial devices
################################################################################

import threading
import time
import datetime
import socket
import serial
import errno
import json
import copy

from queue import Queue
from daemon.logger import *

class Serial_Thread(threading.Thread):
    """
    Title: Serial Thread
    Project: Multiple
    Version: 1.0.0
    Date: Nov 2022
    Author: Zach Leffke, KJ4QLP

    Purpose:
        Interface to serial devices

    Args:
        cfg - Configurations for thread, dictionary format.
        logname - passed from parent thread
        parent - parent thread, used for callbacks
    """
    def __init__ (self, cfg, log_name, parent):
        # threading.Thread.__init__(self)
        threading.Thread.__init__(self, name='SerialThread')
        self._stop  = threading.Event()
        self.cfg    = cfg
        self.parent = parent #Parent is Tracker Class
        # self.setName(self.cfg['name'])
        # self.logger = logging.getLogger(self.cfg['main_log'])
        self.logger = logging.getLogger(log_name) #main logger
        self.logger.info("Initializing {}".format(self.name))

        self.rx_q   = Queue() # Data from device, rx over socket
        self.tx_q   = Queue() # Data to Device, tx over socket

        self.port = self.cfg['port']
        self.baud = self.cfg['baud']
        self._ser_fault = True
        self._err_count = 0
        self.connected = False

        self.tlm = { #Thread control Telemetry message
            "type":"TLM", #Message Type: Thread Telemetry
            "src":"device",
            "connected":False, #Socket Connection Status
            "rx_count":0, #Number of received messages from device
            "tx_count":0, #Number of transmitted messages to device
        }
        self.rx_data = {  #Raw Data Message received from Socket
            'type': 'RX', #Message Type: RX (received message)
            'datetime':None,
            'msg': None
        }
        self.logger.info("Initialized {}".format(self.name))

    def run(self):
        time.sleep(self.cfg['startup_delay'])
        self.logger.info('Launched {:s}'.format(self.name))
        while (not self._stop.isSet()):
            if not self.connected:
                try:
                    self._Open_Serial(self.port)
                except Exception as e:
                    self._handle_serial_exception(e)
                    time.sleep(self.cfg['retry_time'])
            else:
                try:
                    if not self.tx_q.empty():
                        msg = self.tx_q.get()
                        if ((msg['type']=="CMD") and (msg['cmd']=="SEND")):
                            self._send_msg(msg['msg'])
                        elif msg['type']=="CTL":
                            if msg['cmd']=='RESET': self._reset()
                except Exception as e:
                    self._handle_serial_exception(e)
            time.sleep(0.001)

        self.logger.warning('{:s} Terminated'.format(self.name))
        #sys.exit()

    def send_msg(self, msg):
        ''' called by device thread '''
        self.logger.info("TX: {:s}: {:s}".format(msg['name'], msg['cmd']))
        self.ser.flush() #flush buffer
        try:
            self.ser.write(bytes(msg['cmd'], 'ascii'))
            self.tlm['tx_count'] += 1
        except Exception as e:
            self.logger.debug(sys.exc_info())
            self._handle_serial_exception(e)
        if msg['resp'] == None:
            return None
        else:
            return self._recv_data(msg)

    def _recv_data(self, msg=None):
        time.sleep(0.05)
        data = self.ser.readline()
        if len(data) > 0:
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            rx_data = {  #Raw Data Message received from Socket
                'type': 'RX', #Message Type: RX (received message)
                'datetime':ts,
                'msg': {}
            }
            msg['resp'] = data.hex()
            rx_data['msg'] = copy.deepcopy(msg)
            self.logger.info("RX: {:s}".format(msg['resp']))
            self.tlm['rx_count'] += 1
            return rx_data

    def _Open_Serial(self, port):
        self.port = port
        #print self.dev
        self.ser = serial.Serial(port = self.port,
                                 baudrate = self.baud,
                                 timeout = self.cfg['timeout'])
        time.sleep(0.01)
        #print "Opened Serial Port: {:s}".format(self.dev)
        self.logger.info("Opened Serial Port: {:s}".format(self.port))
        self._ser_fault = False
        self.connected = True
        self.tlm['connected']=self.connected
        self.tx_q.queue.clear()
        self.rx_q.queue.clear()
        #self.parent.set_connected_status(self.connected)
        # self.tlm_q.put(self.tlm)
        self.rx_q.put(self.tlm)

    def _handle_serial_exception(self, e):
        #print e
        self.logger.info("Fault with Serial Port: ")
        self.logger.info(e)
        try:
            self.ser.close()
        except:
            pass
        self._err_count += 1
        self._ser_fault = True
        self.connected = False
        self.tlm['connected']=self.connected
        self.rx_q.put(self.tlm)

    ###################################################################
    #                   Thread Control Functions
    ###################################################################
    def stop(self):
        #self.conn.close()
        self.logger.info('{:s} Terminating...'.format(self.name))
        self.tlm['connected']=False
        self.rx_q.put(self.tlm)
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
