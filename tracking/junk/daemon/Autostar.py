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
            'cmd': '',
            'resp': None
        }

    ###################################################################
    #                   ENCODE RAW COMMANDS
    ###################################################################
    def encode_get_elevation(self):
        '''
        Get Telescope Elevation (Altitude)
        Expected Response: sDD*MM# or sDD*MM’SS#
        '''
        msg = self.msg
        msg['cmd']=':GA#'
        msg['resp']='sDD*MM#'
        return msg

    def encode_get_azimuth(self):
        '''
        Get Telescope Azimuth
        Expected Response: sDDD*MM# or sDD*MM’SS#
        '''
        msg = self.msg
        msg['cmd']=':GZ#'
        msg['resp']='sDD*MM#'
        return msg

    def encode_slew(self, dir=None):
        '''
        Slew in indicated direction
        direction options: 'up', down','left','right'
        Expected Response: None
        '''
        msg = self.msg
        if dir == 'up':      msg['cmd']=':Mn#'
        elif dir == 'down':  msg['cmd']=':Ms#'
        elif dir == 'left':  msg['cmd']=':Me#' #Note this is counterintuitive...East implies right
        elif dir == 'right': msg['cmd']=':Mw#' #Note this is counterintuitive...West implies left
        return msg

    def encode_stop_slew(self, dir=None):
        '''
        Halt Slew Command
        direction options: 'up', down','left','right', 'all'
        Expected Response: None
        '''
        msg = self.msg
        if (dir==None) or (dir=='all'): msg['cmd']=':Q#'
        elif dir == 'up':    msg['cmd']=':Qn#'
        elif dir == 'down':  msg['cmd']=':Qs#'
        elif dir == 'left':  msg['cmd']=':Qe#' #Note this is counterintuitive...East implies right
        elif dir == 'right': msg['cmd']=':Qw#' #Note this is counterintuitive...West implies left
        return msg

    def encode_set_target_azimuth(self, az=0):
        '''
        Sets the target Object Azimuth
        Expected Response: 0 - Invalid, 1 - Valid
        '''
        msg = self.msg
        (frac, intnum) = math.modf(az)
        msg['cmd']=':Sz{:03d}*{:02d}#'.format(int(intnum), int(frac*60))
        msg['resp'].update({'0': 'valid','1': 'invalid'})
        return msg

    def encode_set_target_elevation(self, el=0):
        '''
        Set target object elevation (altitude)
        Expected Response:
            0 – Invalid
            1 - Valid
        '''
        msg = self.msg
        (frac, intnum) = math.modf(el)
        msg['cmd']=':Sa{:02d}*{:02d}#'.format(int(intnum), int(frac*60))
        msg['resp'].update({'0': 'valid','1': 'invalid'})
        return msg

    def encode_goto_target_position(self):
        '''
        Slew to target Elevation and Azimuth
        Expected Response: 0 - No Fault, 1 - Fault
        '''
        msg = self.msg
        msg['cmd']=':MA#'
        msg['resp'].update({'0': 'nofault','1': 'fault'})
        return msg

    def encode_focus_inward(self):
        '''
        Start Focuser moving inward (toward objective)
        Expected Response: None
        '''
        msg = self.msg
        msg['cmd']=':F+#'
        return msg

    def encode_focus_outward(self):
        '''
        Start Focuser moving outward (away from objective)
        Expected Response: None
        '''
        msg = self.msg
        msg['cmd']=':F-#'
        return msg

    def encode_focus_stop(self):
        '''
        Halt Focuser Motion
        Expected Response: None
        '''
        msg = self.msg
        msg['cmd']=':FQ#'
        return msg

    def encode_focus_speed(self, speed=False):
        '''
        Set Focus speed
        INPUT: False = Low, True = High
        Expected Response: None
        '''
        msg = self.msg
        if  speed == False: msg['cmd']=':FS#'
        elif speed == True: msg['cmd']=':FF#'
        return msg
        
    ###################################################################
    #                   END ENCODE RAW COMMANDS
    ###################################################################
    #                   DECODE RAW COMMANDS
    ###################################################################

    def decode_target_position(self):
        '''
        Slew to target Elevation and Azimuth
        Expected Response: 0 - No Fault, 1 - Fault
        '''
        msg = self.msg
        msg['cmd']=':MA#'
        msg['resp'].update({'0': 'nofault','1': 'fault'})
