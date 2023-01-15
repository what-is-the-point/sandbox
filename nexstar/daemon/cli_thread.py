#!/usr/bin/env python3
################################################################################
#   Title: KISS Network
# Project: VTGS
# Version: 1.0.0
#    Date: Jan, 2020
#  Author: Zach Leffke, KJ4QLP
# Comments:
#   -This is the user interface thread
################################################################################

import threading
import time
import socket
import errno
import json, yaml
import cmd
import copy
import datetime

from queue import Queue
from daemon.logger import *
#from ax25_utils import *

class Simple_CLI(cmd.Cmd, threading.Thread):
    def __init__(self, cfg, parent):
        super().__init__(completekey="tab", stdin=None, stdout=None)
        threading.Thread.__init__(self)
        self._stop  = threading.Event()
        self.cfg    = cfg
        self.parent = parent
        self.setName(self.cfg['name'])
        self.logger = logging.getLogger(self.cfg['main_log'])

        self.ctl_q = Queue() #Control Queue, for program control
        self.cmd_q = Queue() #Command Queue, for hardware control
        self.logger.info("Initializing {}".format(self.name))

        # self.msgs = self._initialize_packets()
        self.msgs = self._initialize_commands()
        self.prompt='CMD> '

        self.key = None
        self.new_msg = None

        self.cmd_dict={
            "type":"CMD",
            "cmd":"SEND",
            "msg": ''
        }

    def run(self):
        time.sleep(1.5)
        #os.system('reset')
        self.cmdloop('Send Control Commands To Telescope')
        self.logger.warning('{:s} Terminated'.format(self.name))

    def do_list(self, line):
        ''' List avaialable packets '''
        if line: self._list_command(line)
        else:
            disp_len_hex = 30 #number of hex characters per line to display
            disp_len_other = 28
            if self.msgs is not None:
                # print("Available RMQ Messages:")
                #print(self.packets)
                # print(self.msgs)
                banner = "=" * (disp_len_hex+disp_len_other)
                print (banner)
                print("|{:^3s}|{:^15s}|{:^30s}".format("IDX","Command Key", "Description"))
                print (banner)
                for idx,key in enumerate(self.msgs.keys()):
                    # print(idx,key)
                    print ("|{:^3d}| {:14s}| {:29s}".format(idx,key,self.msgs[key]['desc']))
                    #print(i, cmd, '\t',self.packets[i])
                print (banner)
            else:
                print("No RMQ Messages")

    def _chunkstring(self, string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))

    def _list_command(self, cmd):
        if cmd:
            #try to typecast to int
            try: cmd = int(cmd)
            except: pass
            try:
                if isinstance(cmd, int) and (cmd < len(self.msgs)):
                    for idx,key in enumerate(self.msgs.keys()):
                        if idx == cmd:
                            msg = self.msgs[key]
                            # self._send_message(idx, key, self.msgs[key])
                            print(key)
                            print(json.dumps(msg, indent =2))
                else:
                    print("Invalid \'list\' Index: {:d}".format(cmd))
            except Exception as e:
                print(e)
                print("Invalid \'list\' Selection: \'{}\'".format(cmd))
        else:
            print("Invalid \'send\' Selection: \'{:s}\'".format(cmd))
        time.sleep(0.001)

    def do_send(self, cmd):
        '''
        send message over via broker connection
        syntax: send <name> OR send <index>
        get packet name and index using \'list\' command
        '''
        if cmd:
            #try to typecast to int
            try: cmd = int(cmd)
            except: pass
            try:
                if isinstance(cmd, int) and (cmd < len(self.msgs)):
                    for idx,key in enumerate(self.msgs.keys()):
                        if idx == cmd:
                            msg = self.msgs[key]
                            self._send_message(idx, key, self.msgs[key])
                else:
                    print("Invalid \'send\' Index: {:d}".format(cmd))
            except Exception as e:
                print(e)
                print("Invalid \'send\' Selection: \'{}\'".format(cmd))
        else:
            print("Invalid \'send\' Selection: \'{:s}\'".format(cmd))
        time.sleep(0.001)


    def _send_message(self, idx, key, msg):
        self.t_msg = {}
        self.t_msg['head'] = {}
        self.t_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        self.t_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        self.t_msg['head']['src']        = self.cfg['name'] #msg['rmq']['app_id']
        self.t_msg['head']['dest'] = "device"
        self.t_msg['body'] = {}
        self.t_msg['body']['type'] = key
        self.t_msg['body']['params'] = {}

        if key == 'goto':
            az = float(input("  Azimuth: "))
            el = float(input("Elevation: "))
            self.t_msg['body']['params']['azimuth'] = az
            self.t_msg['body']['params']['elevation'] = el
        elif key =='slew':
            print('Direction Options: {}'.format(msg['dir']))
            dir = input("Direction: ")
            if dir not in msg['dir']:
                print('invalid direction')
                return
            else: self.t_msg['body']['params']['dir']=dir
        elif key =='speed':
            print('Speed Options: {}'.format(msg['speed']))
            speed = input("Speed: ")
            if speed not in msg['speed']:
                print('invalid speed')
                return
            else: self.t_msg['body']['params']['speed']=speed
        elif key =='focus_speed':
            print('Speed Options: slow, fast')
            speed = input("Speed: ")
            if speed not in msg['speed']:
                print('invalid speed')
                return
            else: self.t_msg['body']['params']['speed']=speed

        self.t_msg['body']['params']['datetime'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.logger.info("Sending Message: {:s}: {:s}".format(key, json.dumps(self.t_msg)))
        self.cmd_q.put(self.t_msg)

    def do_connect(self,line):
        self.ctl_q.put({"type":"CTL","cmd":"CONNECT"})

    def do_auto(self,line):
        '''
        Automatic TX Control
        Syntax:
            auto <index>
            auto stop
            auto STOP
        '''
        pass

    def do_status(self, line):
        ''' Network Status '''
        print("Querying Network Status...")
        self.ctl_q.put({"type":"CTL","cmd":"STATUS"})
        time.sleep(.1)
        if not self.rx_q.empty(): #Received a message from user
            msg = self.rx_q.get()
            #print("Status: {:s}".format(json.dumps(msg, indent=4)))
            con = "Connected" if msg['connected'] else "Disconnected"
            print("   Program State: {:s}".format(msg['state']))
            print("Connected Status: {:s}".format(con))
            print("       End Point: [{:s}:{:d}]".format(msg['ip'], msg['port']))
            print(" TX Packet Count: {:d}".format(msg['tx_count']))
            print(" RX Packet Count: {:d}".format(msg['rx_count']))
        else:
            print("No Status Feedback Received...")


    def do_reset(self,line):
        ''' reset the program '''
        self.logger.info("Resetting Program.")
        print("Resetting Program....")
        self.ctl_q.put({"type":"CTL","cmd":"RESET"})
        time.sleep(.1)

    def do_clear(self,line):
        ''' clear screen '''
        os.system('reset')

    def do_exit(self, line):
        ''' Terminate the program '''
        self.ctl_q.put({"type":"CTL","cmd":"EXIT"})
        return True

    def do_quit(self, line):
        ''' Terminate the program '''
        self.do_exit('')

    def do_EOF(self):
        return True

    def set_messages(self, msgs):
        self.logger.info("Sent RabbitMQ Messages to CLI Thread")
        self.msgs = msgs
        for idx,key in enumerate(msgs):
            self.logger.debug("--- {:2d} {:s}".format(idx, key))

    # def _initialize_packets(self):
    #     print self.cfg['msgs']
    #     return None

    def _initialize_commands(self):
        if self.cfg['msgs']['base_path'] == "cwd":
            self.cfg['msgs']['base_path'] = os.getcwd()
        fp_cfg = '/'.join([self.cfg['msgs']['base_path'],
                           self.cfg['msgs']['path'],
                           self.cfg['msgs']['file']])
        print (fp_cfg)
        if not os.path.isfile(fp_cfg) == True:
            self.logger.info('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
            sys.exit()
        self.logger.info('Importing configuration File: {:s}'.format(fp_cfg))
        with open(fp_cfg, 'r') as yaml_file:
            cfg = yaml.safe_load(yaml_file)
            yaml_file.close()

        print(json.dumps(cfg))

        return cfg

    def stop(self):
        #self.conn.close()
        self.logger.warning('{:s} Terminating...'.format(self.name))
        #self.do_EOF()

    def stopped(self):
        return self._stop.isSet()
