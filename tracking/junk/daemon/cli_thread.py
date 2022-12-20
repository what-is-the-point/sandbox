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

        self.cmd_q = Queue()
        self.rx_q = Queue()
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
        time.sleep(1)
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


    def _generate_tracking_service_message(self, msg):
        """
        Message is a RabbitMQ Message
        Convert to Generic Tracking Daemon Message
        """
        # print(json.dumps(msg, indent=2))
        t_msg = {}
        t_msg['head'] = {}
        t_msg['head']['session_id'] = msg['rmq']['correlation_id']
        t_msg['head']['src']        = msg['rmq']['app_id']
        t_msg['head']['msg_id']     = msg['rmq']['message_id']
        if "cmd" in msg['rmq']['routing_key']:
            t_msg['head']['dest'] = "device"
        elif "ctl" in msg['rmq']['routing_key']:
            t_msg['head']['dest'] = "daemon"
        else: t_msg['type'] = None

        cmd_key = self.__parse_rmq_key(msg['rmq']['routing_key'])
        if cmd_key:
            t_msg['body']            = {}
            t_msg['body']['type']    = cmd_key
            t_msg['body']['params']  = msg['msg']['parameters']
            self.rx_q.put(t_msg)
        else:
            return None

    def _send_message(self, idx, key, msg):
        print(idx, key, msg)
        del msg['desc']

        if key == 'goto':
            msg['az'] = float(input("  Azimuth: "))
            msg['el'] = float(input("Elevation: "))
        elif key =='slew':
            print('Direction Options: {}'.format(msg['dir']))
            dir = input("Direction: ")
            if dir not in msg['dir']:
                print('invalid direction')
                return
            else: msg['dir']=dir

        cmd_dict={
            "type":"CMD",
            "cmd":"SEND",
            "key": key,
            "msg": msg
        }
        self.logger.info("Sending Message: {:s}:{:s}".format(key, json.dumps(msg)))
        self.cmd_q.put(cmd_dict)

    def _send_message_old(self, idx, key, msg):
        self.new_msg = copy.deepcopy(msg)
        valid = True
        for k,v in msg['parameters'].items():
            if k != "datetime":
                try:
                    depth = len(v.items())
                except:
                    depth = 0

                if depth == 0:
                    value = input("Value for {:s}: ".format(k))
                    value = self._validate_input(k, value)
                    if value == None: valid = False
                    self.new_msg['parameters'][k] = value
                elif depth > 0:
                    print("{:s}:".format(k))
                    for nk, nv in msg['parameters'][k].items():
                        value = input("Value for {:s}: ".format(nk))
                        value = self._validate_input(nk, value)
                        if value == None: valid = False
                        self.new_msg['parameters'][k][nk] = value

        if valid:
            self.key = key
            self._send_valid()
        else:
            self.logger.warning("Command Not Sent: {:s}".format(key))
        time.sleep(0.0001)

    def _send_valid(self):
        '''
        send last valid command
        syntax: send <name> OR send <index>
        get packet name and index using \'list\' command
        '''
        self.new_msg['parameters']['datetime'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        cmd_dict={
            "type":"CMD",
            "cmd":"SEND",
            "key": self.key,
            "msg": self.new_msg
        }
        self.logger.info("Sending Message: {:s}".format(self.key))
        self.cmd_q.put(cmd_dict)

    def do_last_valid(self, line):
        ''' Send last valid command again '''
        if self.new_msg != None: self._send_valid()
        else: self.logger.info("Must send 1 valid command before using")

    def _validate_input(self, k, val):
        bool_keys = ['direction']
        int_keys = ['position', 'rate']
        float_keys = []
        try:
            if any(sub_str in k for sub_str in int_keys):
                new_val = int(val)
            if any(sub_str in k for sub_str in float_keys):
                new_val = float(val)
            if any(sub_str in k for sub_str in bool_keys):
                if isinstance(val, str):
                    if val=="": new_val=True
                    else: new_val = val.lower().capitalize() == "True"
                elif isinstance(val, (float, int)):
                    new_val = bool(val)
            return new_val
        except Exception as e:
            self.logger.warning("invalid datatype for {:s}".format(k))
            self.logger.warning(e)
            return None

    def do_connect(self,line):
        print("Connecting...")

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
        self.cmd_q.put({"type":"CTL","cmd":"STATUS"})
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
        self.cmd_q.put({"type":"CTL","cmd":"RESET"})
        time.sleep(.1)

    def do_clear(self,line):
        ''' clear screen '''
        os.system('reset')

    def do_exit(self, line):
        ''' Terminate the program '''
        self.cmd_q.put({"type":"CTL","cmd":"EXIT"})
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
        ''' setup configuration data '''

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
