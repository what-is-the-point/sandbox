#!/usr/bin/env python3

from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QLabel
import numpy as np
import sys
import time
import datetime
from queue import Queue
import copy

from gui.ControlButtonFrame import *
from gui.lcd_feedback_frame import *
from gui.slew_frame import *
# from gui.feedback_frame import *
from gui.connection_frame import *
from gui.GoToFrame import *
from gui.sync_frame import *
# from gui.gpredict_frame import *
from gui.AzimuthDial import *
from gui.ElevationDial import *
from gui.JoystickFrame import *
from gui.FocuserControlFrame import *
from gui.ADSBFrame import *
from gui.AutoFrame import *
from gui.StatusBar import *


class main_widget(Qt.QFrame):
    def __init__(self):
        super(main_widget, self).__init__()
        self.initUI()
        self.setFrameShape(Qt.QFrame.StyledPanel)

    def initUI(self):
        self.grid = Qt.QGridLayout()
        #self.setLayout(self.grid)

class MainWindow(Qt.QMainWindow):
    def __init__(self, cfg):
        #Qt.QMainWindow.__init__(self)
        super(MainWindow, self).__init__()
        self.setWindowTitle(cfg['title'])
        self.setMinimumSize(700, 425)
        self.resize(700, 425)
        #self.setMinimumWidth(800)
        #self.setMaximumWidth(900)
        #self.setContentsMargins(0,0,0,0)
        self.main_window = main_widget()

        self.cfg = cfg
        self.tx_q = Queue() #commands from gui to main
        self.rx_q = Queue() #feedback to display

        #self.statusBar().showMessage("| Disconnected | Manual | Current Az: 000.0 | Current El: 000.0 |")

        self.init_variables()
        self.init_ui()
        self.setCentralWidget(self.main_tab)
        #self.init_nexstar()

        self.darken()
        self.setFocus()

    def init_variables(self):
        self.connected = False      #TCP/IP Connection Status

        self.az_max     = self.cfg['azimuth']['max']
        self.az_min     = self.cfg['azimuth']['min']
        self.home_az    = self.cfg['azimuth']['home']
        self.tar_az     = self.home_az
        self.cur_az     = 0.0
        self.az_rate    = 0.0

        self.el_max     = self.cfg['elevation']['max']
        self.el_min     = self.cfg['elevation']['min']
        self.home_el    = self.cfg['elevation']['home']
        self.tar_el     = self.home_el
        self.cur_el     = 0.0
        self.com_el     = 0.0
        self.el_rate    = 0.0

        self.callback   = None   #Callback accessor for tracking control

    def init_ui(self):
        self.init_frames()
        self.init_tab()
        # self.init_layout()
        self.init_timers()
        self.connect_signals()
        self.show()

    def init_timers(self):
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.setInterval(1000)

        self.queue_timer = QtCore.QTimer(self)
        self.queue_timer.setInterval(100)

        #Auto Query Timer
        # self.query_timer = QtCore.QTimer(self)
        # self.query_timer.setInterval(self.query_rate*1000)
        # self.query_timer.timeout.connect(self._query_timeout)
        #
        # #Auto Track Timer
        # self.track_timer = QtCore.QTimer(self)
        # self.track_timer.setInterval(self.query_rate*1000)
        # self.track_timer.timeout.connect(self._track_timeout)

    def _send_dev_command(self, msg):
        self.t_msg = {}
        self.t_msg['head'] = {}
        self.t_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        self.t_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        self.t_msg['head']['src']        = msg['src']
        self.t_msg['head']['dest'] = "device"
        self.t_msg['body'] = {}

        if msg['cmd'] == 'slew':
            # print(msg)
            self._handle_joystick_slew(msg)
        elif msg['cmd'] == 'focus':
            self._handle_focus_motion(msg)
        else:
            self.t_msg['body']['type'] = msg['cmd']
            self.t_msg['body']['params'] = msg['params']
            self.tx_q.put(self.t_msg)

    def _handle_focus_motion(self,msg):
        print('Handle Focus Motion....set speed then send command....')
        print(msg)
        print('to be implemented.......')
        spd_msg = {}
        spd_msg['head'] = {}
        spd_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        spd_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        spd_msg['head']['src']        = msg['src']
        spd_msg['head']['dest'] = "device"
        spd_msg['body'] = {}
        spd_msg['body']['params'] = {}
        spd_msg['body']['params']['datetime'] = msg['params']['datetime']
        spd_msg['body']['params']['speed'] = msg['params']['speed']
        spd_msg['body']['type'] = 'focus_speed'
        self.tx_q.put(spd_msg)

        move_msg = {}
        move_msg['head'] = {}
        move_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        move_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        move_msg['head']['src']        = msg['src']
        move_msg['head']['dest'] = "device"
        move_msg['body'] = {}
        move_msg['body']['params'] = {}
        move_msg['body']['params']['datetime'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        move_msg['body']['type'] = 'focus_{:s}'.format(msg['params']['direction'])
        self.tx_q.put(move_msg)


    def _handle_joystick_slew(self, msg):
        new_msg = {}
        new_msg['head'] = {}
        new_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        new_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        new_msg['head']['src']        = msg['src']
        new_msg['head']['dest'] = "device"
        new_msg['body'] = {}

        rho_ratio = msg['params']['rho']/msg['params']['rho_max']
        theta = msg['params']['theta']

        new_msg['body']['params'] = {}
        if rho_ratio ==0:
            new_msg['body']['type'] = 'stop'
            new_msg['body']['params']['datetime'] = msg['params']['datetime']
            self.tx_q.put(new_msg)
            return
        elif rho_ratio < 1.0/3.0:
            speed = 'slow'
        elif (rho_ratio >= 1.0/3.0) and (rho_ratio < 0.75):
            speed = 'medium'
        elif rho_ratio >= 0.75:
            speed = 'fast'

        new_msg['body']['type'] = 'speed'
        new_msg['body']['params'] = {}
        new_msg['body']['params']['datetime'] = msg['params']['datetime']
        new_msg['body']['params']['speed'] = speed
        print(new_msg)
        self.tx_q.put(new_msg)
        # time.sleep(0.01)
        lr_msg = {}
        lr_msg['head'] = {}
        lr_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        lr_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        lr_msg['head']['src']        = msg['src']
        lr_msg['head']['dest'] = "device"
        lr_msg['body'] = {}
        lr_msg['body']['type'] = 'slew'
        lr_msg['body']['params'] = {}
        lr_msg['body']['params']['datetime'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if abs(theta) <= 67.5:
            lr_msg['body']['params']['dir'] = 'r'
        elif abs(theta) >= 112.5:
            lr_msg['body']['params']['dir'] = 'l'
        self.tx_q.put(lr_msg)

        ud_msg = {}
        ud_msg['head'] = {}
        ud_msg['head']['session_id'] = None #msg['rmq']['correlation_id']
        ud_msg['head']['msg_id']     = None #msg['rmq']['message_id']
        ud_msg['head']['src']        = msg['src']
        ud_msg['head']['dest'] = "device"
        ud_msg['body'] = {}
        ud_msg['body']['type'] = 'slew'
        ud_msg['body']['params'] = {}
        ud_msg['body']['params']['datetime'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if (abs(theta)>22.5) and (abs(theta)<157.5):
            if theta < 0:
                ud_msg['body']['params']['dir'] = 'd'
            elif theta > 0:
                ud_msg['body']['params']['dir'] = 'u'
            self.tx_q.put(ud_msg)





    def _send_adsb_command(self, msg):
        self.tx_q.put(msg)


    def connect_signals(self):
        #self.update_timer.timeout.connect(self.auto_query_timeout)
        self.update_timer.timeout.connect(self.gauge_test)
        # self.update_timer.start()

        self.queue_timer.timeout.connect(self.check_gui_queue)
        self.queue_timer.start()

        self.JoystickFrame.reportRates.connect(self._send_dev_command)
        self.ConnectionFrame.connectFrameSignal.connect(self._send_dev_command)
        self.GoToFrame.gotoSignal.connect(self._send_dev_command)
        self.GoToFrame.stopSignal.connect(self._send_dev_command)
        self.GoToFrame.querySignal.connect(self._send_dev_command)
        self.FocuserFrame.focusSignal.connect(self._send_dev_command)
        self.ADSBConnFrame.ADSBConnectSignal.connect(self._send_adsb_command)
        self.ADSBTargetSelectFrame.ICAOTargetSignal.connect(self._send_adsb_command)
        self.ObserverFrame.locationUpdateSignal.connect(self._send_adsb_command)

    def check_gui_queue(self):
        if not self.rx_q.empty():
            msg = self.rx_q.get()
            # print(msg)
            if msg['src']=='device': self._update_device(msg)
            elif msg['src']=='adsb.sbs1': self._update_adsb_tlm(msg)
            elif msg['src']=='track': self._update_adsb_tracking(msg['msg'])


    def _update_adsb_tracking(self, msg):
        # print(msg)
        self.ADSBFeedbackFrame.update_data(msg)
        self.StatusBar.update_icao(msg['icao'])
        self.StatusBar.update_target_angle(msg['azimuth'], msg['elevation'], msg['range'])
        self.AzimuthDial.update_target_angle(msg['azimuth'])
        self.ElevationDial.update_target_angle(msg['elevation'])
        self.GoToFrame.update_target_angle(msg['azimuth'], msg['elevation'])

    def _update_adsb_tlm(self, msg):
        if msg['type']=='TLM':
            self.sbs1_connected = bool(msg['connected'])
            self._update_adsb_conn_status()

    def _update_adsb_conn_status(self):
        self.ADSBConnFrame.update_sbs1_connection_state(self.sbs1_connected)
        self.StatusBar.update_sbs1_connection_state(self.sbs1_connected)

    def _update_device(self, msg):
        print(msg)
        if msg['type']=='TLM':
            self.dev_connected = bool(msg['connected'])
            self._update_dev_conn_status()
        elif msg['type']=='RX':
            self.cur_az = msg['cur_az']
            self.cur_el = msg['cur_el']
            self.com_az = msg['tar_az']
            self.com_el = msg['tar_el']
            self._update_gui()

    def _update_gui(self):
        self.AzimuthDial.update_current_angle(self.cur_az)
        self.AzimuthDial.update_command_angle(self.com_az)
        self.AzimuthDial.update_target_angle(self.tar_az)
        self.ElevationDial.update_current_angle(self.cur_el)
        self.ElevationDial.update_command_angle(self.com_el)
        self.ElevationDial.update_target_angle(self.tar_el)

        self.StatusBar.update_current_angle(self.cur_az, self.cur_el)
        self.StatusBar.update_command_angle(self.com_az, self.com_el)


    def _update_dev_conn_status(self):
        self.ConnectionFrame.update_connection_state(self.dev_connected)
        self.StatusBar.update_dev_conn_status(self.dev_connected)

    def gauge_test(self):
        self.cur_az = np.random.uniform(low=0, high=360)
        self.com_az = np.random.uniform(low=0, high=360)
        self.tar_az = np.random.uniform(low=0, high=360)
        self.AzimuthDial.update_current_angle(self.cur_az)
        self.AzimuthDial.update_command_angle(self.com_az)
        self.AzimuthDial.update_target_angle(self.tar_az)

        self.cur_el = np.random.uniform(low=-5, high=95)
        self.com_el = np.random.uniform(low=-5, high=95)
        self.tar_el = np.random.uniform(low=-5, high=95)
        self.ElevationDial.update_current_angle(self.cur_el)
        self.ElevationDial.update_command_angle(self.com_el)
        self.ElevationDial.update_target_angle(self.tar_el)

    def auto_query_timeout(self):
        [self.cur_az, self.cur_el] = self.ns.getPosition()
        #[self.cur_ra, self.cur_dec] = self.ns.getPosition(coordinateMode=NexstarCoordinateMode.RA_DEC)
        self.track_mode = self.ns.getTrackingMode()
        self.gtip = self.ns.getGotoInProgress()

        self.fb_fr.update_az_el(self.cur_az, self.cur_el)
        #self.fb_fr.update_ra_dec(self.cur_ra, self.cur_dec)
        self.fb_fr.update_track_mode(self.track_mode)
        self.fb_fr.update_gtip(self.gtip)

    ##### GUI Update Operations #####
    def _UpdateAzimuthElevation(self):
        self.AzimuthDial.update_target_angle(self.tar_az)
        # self.AzimuthLCD.set_target(self.tar_az)

        self.ElevationDial.update_target_angle(self.tar_el)
        # self.ElevationLCD.set_target(self.tar_el)

    ##### INCREMENT/DECREMENT TARGET VALUE OPERATIONS ############
    def AzIncDec(self,val):
        self.tar_az = self.tar_az + val
        if self.tar_az > self.az_max: self.tar_az = self.az_max
        if self.tar_az < self.az_min: self.tar_az = self.az_min
        #self.updateAzDial
        print("Increment/Decrement Tar AZ:", self.tar_az)
        self._UpdateAzimuthElevation()

    def ElIncDec(self,val):
        self.tar_el = self.tar_el + val
        if self.tar_el > 190: self.tar_el = 190.0
        if self.tar_el < -10:   self.tar_el = -10.0
        #self.updateAzDial
        print("Increment/Decrement Tar EL:", self.tar_el)
        self._UpdateAzimuthElevation()


    ##### SLEW OPERATIONS ############
    ##### GOTO OPERATIONS ############

    def init_frames(self):
        #self.pred_fr = gpredict_frame(self.cfg['gpredict'], self)
        if self.cfg['con']['type'] == 'net':
            self.ConnectionFrame = ConnectionFrameNet(self.cfg['con'])
        elif self.cfg['con']['type'] == 'serial':
            self.ConnectionFrame = ConnectionFrameSerial(self.cfg['con'])

        self.GoToFrame      = GoToFrame(az=self.home_az,el=self.home_el, parent=self)
        self.JoystickFrame  = JoystickFrame(cfg=self.cfg['joystick'], parent=self)
        self.AzimuthDial    = AzimuthDialFrame(lbl="Azimuth", cfg=self.cfg['azimuth'])
        self.ElevationDial  = ElevationDialFrame(lbl="Elevation", cfg=self.cfg['elevation'])
        self.FocuserFrame   = FocuserControlFrame(cfg=self.cfg['focuser'])
        self.ADSBConnFrame  = ADSBConnFrame(cfg=self.cfg['adsb'])
        self.ADSBFeedbackFrame = ADSBFeedbackFrame(name='ADSB Data', parent=self)
        self.ADSBTargetSelectFrame = ADSBTargetSelectFrame(parent=self)
        self.AutoFrame = AutoFrame(parent=self)
        self.StatusBar = StatusBar(parent=self)
        self.ObserverFrame = ObserverLocationFrame(cfg=self.cfg['observer'], parent=self)

        self._UpdateAzimuthElevation()

    def init_tab(self):
        self.main_grid = Qt.QGridLayout()
        self.main_tab = QTabWidget()
        self.adsb_tab = QWidget()
        self.ctrl_tab = QWidget()
        self.cam_tab = QWidget()

        self.main_tab.addTab(self.ctrl_tab, "Motion Control")
        self.main_tab.addTab(self.adsb_tab, "ADSB Control")
        self.main_tab.addTab(self.cam_tab, "Camera Control")

        self.main_tab.setStyleSheet("QTabBar {font:12pt; \
                                              color:rgb(255,0,0); \
                                              background-color:rgb(75,75,75);} \
                                     QGroupBox {font:10pt; \
                                                color:rgb(255,0,0); \
                                                background-color:rgb(45,47,44);; }")

        self.ctrl_tab.layout = Qt.QGridLayout()
        self.ctrl_tab.layout.addWidget(self.ConnectionFrame ,0,0,1,2)
        self.ctrl_tab.layout.addWidget(self.JoystickFrame   ,1,0,4,2)

        self.ctrl_tab.layout.addWidget(self.AzimuthDial     ,0,2,4,3)
        self.ctrl_tab.layout.addWidget(self.ElevationDial   ,0,5,4,3)

        self.ctrl_tab.layout.addWidget(self.GoToFrame       ,4,2,2,3)
        self.ctrl_tab.layout.addWidget(self.AutoFrame       ,4,5,1,3)
        # self.ctrl_tab.layout.addWidget(self.AutoFrame       ,4,5,1,3)

        self.ctrl_tab.layout.setRowStretch(2,1)
        self.ctrl_tab.layout.setRowStretch(5,1)
        self.ctrl_tab.layout.setColumnStretch(1,5)
        self.ctrl_tab.layout.setColumnStretch(2,7)
        self.ctrl_tab.layout.setColumnStretch(6,7)
        # self.ctrl_tab.layout.setColumnStretch(6,2)

        #

        self.ctrl_tab.setLayout(self.ctrl_tab.layout)

        self.adsb_tab.layout = Qt.QGridLayout()
        self.adsb_tab.layout.addWidget(self.ADSBConnFrame,0,0,1,1)
        self.adsb_tab.layout.addWidget(self.ADSBFeedbackFrame,0,1,3,1)
        self.adsb_tab.layout.addWidget(self.ADSBTargetSelectFrame,1,0,1,1)
        self.adsb_tab.layout.addWidget(self.ObserverFrame,0,2,1,1)
        self.adsb_tab.layout.setColumnStretch(3,1)
        # self.adsb_tab.layout.setRowStretch(2,1)
        self.adsb_tab.layout.setRowStretch(4,1)
        self.adsb_tab.setLayout(self.adsb_tab.layout)


        lbl = QLabel('TO BE IMPLEMENTED...')
        lbl.setStyleSheet("QLabel {font:20pt; color:rgb(255,0,0);}")
        self.cam_tab.layout = Qt.QGridLayout()
        self.cam_tab.layout.addWidget(lbl,0,0,1,1)
        self.cam_tab.layout.addWidget(self.FocuserFrame,1,0,1,1)
        self.cam_tab.layout.setRowStretch(0,10)
        self.cam_tab.setLayout(self.cam_tab.layout)

        self.setStatusBar(self.StatusBar)




    def init_layout(self):
        vbox1 = Qt.QVBoxLayout()

        self.main_grid = Qt.QGridLayout()

        # self.main_grid.addWidget(self.ConnectionFrame,0,0,1,1)
        # self.main_grid.addWidget(self.ADSBConnFrame,1,0,1,1)
        # self.main_grid.addWidget(self.GoToFrame, 2,0,1,1)
        # self.main_grid.addWidget(self.FocuserFrame,3,0,1,1)
        vbox1.addWidget(self.ConnectionFrame)
        vbox1.addWidget(self.ADSBConnFrame)
        vbox1.addWidget(self.GoToFrame)
        vbox1.addWidget(self.FocuserFrame)

        vbox1.addStretch(1)
        self.main_grid.addLayout(vbox1,0,0,3,1)

        self.main_grid.addWidget(self.AzimuthDial,0,1,2,1)
        self.main_grid.addWidget(self.ElevationDial,0,2,2,1)
        self.main_grid.addWidget(self.JoystickFrame, 2,1,2,1)

        self.main_grid.setColumnStretch(0,1)
        self.main_grid.setColumnStretch(1,2)
        self.main_grid.setColumnStretch(2,2)
        # self.main_grid.setColumnStretch(3,2)
        # self.main_grid.setRowStretch(0,1)
        # self.main_grid.setRowStretch(0,1)

        self.main_window.setLayout(self.main_grid)

    def init_layout_old(self):
        vbox1 = Qt.QVBoxLayout()

        self.main_grid = Qt.QGridLayout()
        self.main_grid.addWidget(self.JoystickFrame, 0,0,1,1)
        self.main_grid.addWidget(self.GoToFrame, 1,0,1,1)
        self.main_grid.addWidget(self.FocuserFrame,2,0,1,1)

        self.main_grid.addWidget(self.AzimuthDial,0,1,1,1)
        self.main_grid.addWidget(self.ElevationDial,0,2,1,1)

        self.main_grid.addWidget(self.ConnectionFrame,1,1,2,1)
        self.main_grid.addWidget(self.ADSBConnFrame,1,2,2,1)

        self.main_grid.setColumnStretch(0,1)
        self.main_grid.setColumnStretch(1,1)
        self.main_grid.setColumnStretch(2,1)
        self.main_grid.setRowStretch(0,2)

        self.main_window.setLayout(self.main_grid)

    def init_layout_oldest(self):
        vbox1 = Qt.QVBoxLayout()
        vbox1.addWidget(self.ConnectionFrame)
        vbox1.addWidget(self.GoToFrame)
        vbox1.addWidget(self.FocuserFrame)

        self.main_grid = Qt.QGridLayout()
        self.main_grid.addLayout(vbox1, 0,0,1,1)
        self.main_grid.addWidget(self.JoystickFrame,1,0,1,1)
        self.main_grid.addWidget(self.AzimuthDial,0,1,1,1)
        self.main_grid.addWidget(self.ElevationDial,0,2,1,1)

        self.main_grid.setColumnStretch(0,1)
        self.main_grid.setColumnStretch(1,1)
        self.main_grid.setColumnStretch(2,1)
        # self.main_grid.setRowStretch(3,1)
        self.main_window.setLayout(self.main_grid)

    def set_callback(self, callback):
        self.callback = callback

    def closeEvent(self, *args, **kwargs):

        print("Closing GUI")
        self.tx_q.put({"type":"CTL","cmd":"EXIT"})
        self.update_timer.stop()

    def darken(self):
        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Background,QColor(45,47,44))
        palette.setColor(Qt.QPalette.WindowText,QtCore.Qt.black)
        palette.setColor(Qt.QPalette.Text,QColor(255,255,255))
        self.setPalette(palette)

    def utc_ts(self):
        return str(date.utcnow()) + " UTC | GUI | "
