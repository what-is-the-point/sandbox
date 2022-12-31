#!/usr/bin/env python3
#################################################
#   Title: Celestron Focus Motor Encoding/Decoding Class
# Project: Multiple (VTGS)
# Version: 0.0.1
#    Date: Nov, 2022
#  Author: Zach Leffke, KJ4QLP
# Comment:
# - Focus Motor Class for encoding/decoding
#   Celestron Focus Motor Messages
#################################################

import math
import string
import time
import sys
import os
import threading
import json
import struct
import binascii
import numpy as np
import copy

from daemon.logger import *
from queue import Queue
#import track_thread
#from daemon import network_thread

class Autostar(object):
    """
    Class for encoding/decoding Celestron Focus Motor Messages
    """
    def __init__(self):
        self.msg = {
            'name':'',
            'cmd': '',
            'resp': None
        }

        self.cur_az = 0.0
        self.cur_el = 0.0
        self.com_az = 0.0
        self.com_el = 0.0
        self.tar_az = 0.0
        self.tar_el = 0.0
        self.az_valid = True
        self.el_valid = True
        self.slew_speed = 4
        self.focus_speed = 'fast'
        self.goto_fault = False


    def get_status(self):
        status = {
            'type':'autostar',
            'src':'device',
            'cur_az': self.cur_az,
            'cur_el': self.cur_el,
            'tar_az': self.tar_az,
            'tar_el': self.tar_el,
            'slew_speed': self.slew_speed,
            'focus_speed': self.focus_speed,
            'goto_fault': self.goto_fault
        }
        return status

    ###################################################################
    #                   ENCODE RAW COMMANDS
    ###################################################################
    def encode_get_elevation(self):
        '''
        Get Telescope Elevation (Altitude)
        Expected Response: sDD*MM# or sDD*MM’SS#
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='get_el'
        msg['cmd']=':GA#'
        msg['resp']='sDD*MM#'
        return msg

    def encode_get_azimuth(self):
        '''
        Get Telescope Azimuth
        Expected Response: sDDD*MM# or sDD*MM’SS#
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='get_az'
        msg['cmd']=':GZ#'
        msg['resp']='sDDD*MM#'
        return msg

    def encode_slew(self, dir=None):
        '''
        Slew in indicated direction
        direction options: 'up', down','left','right'
        Expected Response: None
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='slew'
        if   dir == 'u': msg['cmd']=':Mn#'
        elif dir == 'd': msg['cmd']=':Ms#'
        elif dir == 'l': msg['cmd']=':Me#' #Note this is counterintuitive...East implies right
        elif dir == 'r': msg['cmd']=':Mw#' #Note this is counterintuitive...West implies left
        return msg

    def encode_set_slew_speed(self, speed='slow'):
        '''
        Slew in indicated direction
        speed options: slow, medium, fast
        Expected Response: 0 - Invalid, 1 - Valid
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='speed'
        if   speed == 'slow':   msg['cmd']=':Sw2#'
        elif speed == 'medium': msg['cmd']=':Sw3#'
        elif speed == 'fast':   msg['cmd']=':Sw4#'
        msg['resp']={'0': 'valid','1': 'invalid'}
        return msg

    def encode_stop_slew(self, dir=None):
        '''
        Halt Slew Command
        direction options: u-up, d-down, l-left, r-right, all
        Expected Response: None
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='stop'
        if (dir==None) or (dir=='all'): msg['cmd']=':Q#'
        elif dir == 'u': msg['cmd']=':Qn#'
        elif dir == 'd': msg['cmd']=':Qs#'
        elif dir == 'l': msg['cmd']=':Qe#' #Note this is counterintuitive...East implies right
        elif dir == 'r': msg['cmd']=':Qw#' #Note this is counterintuitive...West implies left
        return msg

    def encode_set_tar_az(self, az=0.0):
        '''
        Sets the target Object Azimuth
        Expected Response: 0 - Invalid, 1 - Valid
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='set_az'
        self.tar_az = az
        (frac, intnum) = math.modf(az)
        msg['cmd']=':Sz{:03d}*{:02d}#'.format(int(intnum), int(frac*60))
        msg['resp']={'0': 'valid','1': 'invalid'}
        return msg

    def encode_set_tar_el(self, el=0.0):
        '''
        Set target object elevation (altitude)
        Expected Response:
            0 – Invalid
            1 - Valid
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='set_el'
        self.tar_el = el
        (frac, intnum) = math.modf(el)
        msg['cmd']=':Sa{:02d}*{:02d}#'.format(int(intnum), int(frac*60))
        msg['resp']={'0': 'valid','1': 'invalid'}
        return msg

    def encode_goto_target_position(self):
        '''
        Slew to target Elevation and Azimuth
        Expected Response: 0 - No Fault, 1 - Fault
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='goto'
        msg['cmd']=':MA#'
        msg['resp']={'0': 'nofault','1': 'fault'}
        return msg

    def encode_focus_inward(self):
        '''
        Start Focuser moving inward (toward objective)
        Expected Response: None
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='focus_in'
        msg['cmd']=':F+#'
        return msg

    def encode_focus_outward(self):
        '''
        Start Focuser moving outward (away from objective)
        Expected Response: None
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='focus_out'
        msg['cmd']=':F-#'
        return msg

    def encode_focus_stop(self):
        '''
        Halt Focuser Motion
        Expected Response: None
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='focus_stop'
        msg['cmd']=':FQ#'
        return msg

    def encode_focus_speed(self, speed='fast'):
        '''
        Set Focus speed
        INPUT: slow, fast
        Expected Response: None
        '''
        msg = copy.deepcopy(self.msg)
        msg['name']='focus_speed'
        if   speed == 'slow':  msg['cmd']=':FS#'
        elif speed == 'fast': msg['cmd']=':FF#'
        self.focus_speed=speed
        return msg

    ###################################################################
    #                   END ENCODE RAW COMMANDS
    ###################################################################
    #                   DECODE RAW COMMANDS
    ###################################################################

    def decode(self, msg):
        buff = binascii.unhexlify(msg['resp'])
        if msg['name'] == 'get_az':
            # buff = binascii.unhexlify(msg['resp'])
            deg = float(buff[0:3])
            min = float(buff[4:6])
            self.cur_az = round(deg + min/60.0, 3)
        elif msg['name'] == 'get_el':
            # buff = binascii.unhexlify(msg['resp'])
            deg = float(buff[0:3])
            min = float(buff[4:6])
            self.cur_el = round(deg + min/60.0, 3)
        elif msg['name'] == 'goto':
            # buff = binascii.unhexlify(msg['resp'])
            self.goto_fault = (not bool(buff))
        elif msg['name'] == 'set_az':
            self.az_valid = (bool(buff))
            if self.az_valid: self.tar_az = msg['tar_az']
        elif msg['name'] == 'set_el':
            self.el_valid = (bool(buff))
            if self.el_valid: self.tar_el = msg['tar_el']
        elif msg['name'] == 'speed':
            self.speed_valid = (bool(buff))
            if self.speed_valid:
                if '2' in msg['cmd']: self.slew_speed = 2
                if '3' in msg['cmd']: self.slew_speed = 3
                if '4' in msg['cmd']: self.slew_speed = 4
