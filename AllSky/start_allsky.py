#!/usr/bin/env python3
########################################################
#   Title: AllSky Start Script
#  Thread: 
# Project: UAP AllSky Detector
# Version: 0.0.1
#    Date: August 2023
#  Author: Carson Horne based on code from Zach Leffke, KJ4QLP
# Comment:Initializes main thread and starts logging
########################################################


import socket
import os
import string
import sys
import time
import argparse
import datetime
import json, csv, yaml
import subprocess
from binascii import *

from daemon.main_thread import *
#from gui.generic_gui import *
#from track_gui import *
#from nexstar import *

def import_configs_yaml(args):
    ''' setup configuration data '''
    fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    print (fp_cfg)
    if not os.path.isfile(fp_cfg) == True:
        print('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
        sys.exit()
    print('Importing configuration File: {:s}'.format(fp_cfg))
    with open(fp_cfg, 'r') as yaml_file:
        cfg = yaml.safe_load(yaml_file)
        yaml_file.close()

    if cfg['main']['base_path'] == 'cwd':
        cfg['main']['base_path'] = os.getcwd()
    return cfg

def configure_logs(cfg):
    #configure main log configs
    log_name = '.'.join([cfg['main']['name'],cfg['main']['log']['name']])
    log_path = '/'.join([cfg['main']['log']['path'],startup_ts])
    cfg['main']['log'].update({
        'name':log_name,
        'startup_ts':startup_ts,
        'path':log_path
    })
    if not os.path.exists(cfg['main']['log']['path']):
        os.makedirs(cfg['main']['log']['path'])

    #configure thread specific logs
    for key in cfg['thread_enable'].keys():
        #first tell the sub thread where to find main log
        cfg[key].update({
            'main_log':cfg['main']['log']['name']
        })

    return cfg


if __name__ == '__main__':
    """ Main entry point to start the service. """
    startup_ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    #--------START Command Line argument parser------------------------------------------------------
    parser = argparse.ArgumentParser(description="Tracking Control Daemon",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cwd = os.getcwd()
    cfg_fp_default = '/'.join([cwd, 'config'])
    cfg = parser.add_argument_group('Configuration File')
    cfg.add_argument('--cfg_path',
                       dest='cfg_path',
                       type=str,
                       default='/'.join([os.getcwd(), 'config']),
                       help="Daemon Configuration File Path",
                       action="store")
    cfg.add_argument('--cfg_file',
                       dest='cfg_file',
                       type=str,
                       default="AllSky_config.yaml",
                       help="Daemon Configuration File",
                       action="store")
    args = parser.parse_args()
#--------END Command Line argument parser------------------------------------------------------
    subprocess.run(["reset"])
    cfg = import_configs_yaml(args)

    cfg = configure_logs(cfg)
    main_thread = Main_Thread(cfg)
    main_thread.daemon = True
    main_thread.run()
    sys.exit()




















    #
    # fp_cfg = '/'.join([args.cfg_path,args.cfg_file])
    # print (fp_cfg)
    # if not os.path.isfile(fp_cfg) == True:
    #     print('ERROR: Invalid Configuration File: {:s}'.format(fp_cfg))
    #     sys.exit()
    # print('Importing configuration File: {:s}'.format(fp_cfg))
    # with open(fp_cfg, 'r') as json_data:
    #     cfg = json.load(json_data)
    #     json_data.close()



    sys.exit()


        # cfg[key]['log'].update({
        #     'path':cfg['main']['log']['path'],
        #     'name':log_name,
        #     'startup_ts':startup_ts,
        # })

    #print (json.dumps(cfg, indent=4))

    #create nexstar object
    #ns = NexstarHandController(cfg['nexstar']['dev'])
    app = Qt.QApplication(sys.argv)
    app.setStyle('Windows')
    win = MainWindow(cfg)
    #win.set_callback(track)

    #win.setGpredictCallback(gpred)

    sys.exit(app.exec_())
    #ns.close()
    sys.exit()
