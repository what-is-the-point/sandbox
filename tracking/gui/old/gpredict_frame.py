#!/usr/bin/env python3

from PyQt5 import Qt
from PyQt5 import QtCore
import math

class gpredict_frame(Qt.QFrame):
    def __init__(self, cfg, parent=None):
        super(gpredict_frame, self).__init__()
        self.cfg = cfg
        self.parent = parent
        self.initVariables()
        self.initUI()

    def initVariables(self):
        self.pred_az = 0.0
        self.pred_el = 0.0
        self.pred_ip = self.cfg['ip']
        self.pred_port = self.cfg['port']
        self.gpredict  = None     #Callback accessor for gpredict thread control
        self.pred_conn_state = 0   #Gpredict Connection Status, 0=Disconnected, 1=Listening, 2=Connected
        self.autoTrack = False    #auto track mode, True = Auto, False = Manual

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        self.initWidgets()
        self.connect_signals()

    def initWidgets(self):
        self.gpredict_ip_le = Qt.QLineEdit()
        self.gpredict_ip_le.setText(self.pred_ip)
        self.gpredict_ip_le.setInputMask("000.000.000.000;")
        self.gpredict_ip_le.setEchoMode(Qt.QLineEdit.Normal)
        self.gpredict_ip_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.gpredict_ip_le.setMaxLength(15)
        self.gpredict_ip_le.setFixedHeight(20)
        self.gpredict_ip_le.setFixedWidth(125)

        self.gpredict_port_le = Qt.QLineEdit()
        self.gpredict_port_le.setText(str(self.pred_port))
        self.port_validator = Qt.QIntValidator()
        self.port_validator.setRange(0,65535)
        self.gpredict_port_le.setValidator(self.port_validator)
        self.gpredict_port_le.setEchoMode(Qt.QLineEdit.Normal)
        self.gpredict_port_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.gpredict_port_le.setMaxLength(5)
        self.gpredict_port_le.setFixedWidth(50)
        self.gpredict_port_le.setFixedHeight(20)

        label = Qt.QLabel('Status:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        label.setFixedHeight(10)
        self.pred_status_lbl = Qt.QLabel('Disconnected')
        self.pred_status_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pred_status_lbl.setStyleSheet("QLabel {font-weight:bold; color:rgb(255,0,0);}")
        self.pred_status_lbl.setFixedWidth(125)
        self.pred_status_lbl.setFixedHeight(10)

        self.predict_button = Qt.QPushButton("Start Predict Server")
        self.predict_button.setFixedHeight(20)

        lbl1 = Qt.QLabel('Az:')
        lbl1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl1.setStyleSheet("QLabel {color:rgb(255,255,255)}")
        lbl1.setFixedWidth(25)
        lbl1.setFixedHeight(10)

        lbl2 = Qt.QLabel('El:')
        lbl2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl2.setStyleSheet("QLabel {color:rgb(255,255,255)}")
        lbl2.setFixedWidth(25)
        lbl2.setFixedHeight(10)

        self.pred_az_lbl = Qt.QLabel('XXX.X')
        self.pred_az_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pred_az_lbl.setStyleSheet("QLabel {color:rgb(255,255,255)}")
        self.pred_az_lbl.setFixedWidth(50)
        self.pred_az_lbl.setFixedHeight(10)

        self.pred_el_lbl = Qt.QLabel('XXX.X')
        self.pred_el_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pred_el_lbl.setStyleSheet("QLabel {color:rgb(255,255,255)}")
        self.pred_el_lbl.setFixedWidth(50)
        self.pred_el_lbl.setFixedHeight(10)

        self.auto_track_cb = Qt.QCheckBox("Auto Track")
        self.auto_track_cb.setStyleSheet("QCheckBox { background-color:rgb(0,0,0); color:rgb(255,255,255); }")
        self.auto_track_cb.setFixedHeight(20)

        hbox1 = Qt.QHBoxLayout()
        hbox1.addWidget(self.gpredict_ip_le)
        hbox1.addWidget(self.gpredict_port_le)

        hbox2 = Qt.QHBoxLayout()
        hbox2.addWidget(label)
        hbox2.addWidget(self.pred_status_lbl)

        hbox3 = Qt.QHBoxLayout()
        hbox3.addWidget(lbl1)
        hbox3.addWidget(self.pred_az_lbl)

        hbox4 = Qt.QHBoxLayout()
        hbox4.addWidget(lbl2)
        hbox4.addWidget(self.pred_el_lbl)

        vbox1 = Qt.QVBoxLayout()
        vbox1.addLayout(hbox3)
        vbox1.addLayout(hbox4)

        hbox5 = Qt.QHBoxLayout()
        hbox5.addWidget(self.auto_track_cb)
        hbox5.addLayout(vbox1)

        vbox = Qt.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addWidget(self.predict_button)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox5)

        self.setLayout(vbox)

    def connect_signals(self):
        #Gpredict Signals
        self.predict_button.clicked.connect(self.predict_button_event)
        #QtCore.QObject.connect(self.gpredict_ip_le, QtCore.SIGNAL('editingFinished()'), self.update_predict_ip)
        #QtCore.QObject.connect(self.gpredict_port_le, QtCore.SIGNAL('editingFinished()'), self.update_predict_port)
        #QtCore.QObject.connect(self.predict_timer, QtCore.SIGNAL('timeout()'), self.update_predict_status)

    ##### GPREDICT and AUTO TRACK FUNCTIONS #####
    # Functions that deal with Grpedict and auto tracking
    def predict_button_event(self):
        if self.pred_conn_state == 0:  #Disconnected, Start Connection Thread
            self.gpredict = Gpredict_Thread(self, self.pred_ip, self.pred_port,1)
            self.gpredict.daemon = True
            self.gpredict.start()
            #self.pred_conn_state = 1 #listening
            #self.update_predict_status()
            self.predict_timer.start()
        elif ((self.pred_conn_state == 1) or (self.pred_conn_state == 2)):
            self.gpredict.stop()
            self.gpredict.join()
            self.predict_timer.stop()
            self.set_predict_conn_state(0)
            self.update_predict_status()

    def update_predict_ip(self):
        self.pred_ip=self.gpredict_ip_le.text()

    def update_predict_port(self):
        self.pred_port = int(self.gpredict_port_le.text())

    def set_predict_conn_state(self, state):
        #function called by gpredict thread
        self.pred_conn_state = state
        #self.update_predict_status()

    def predict_callback_set(self, az, el):
        #function called by gpredict thread
        #sets target angles when auto tracking
        self.pred_az = az
        self.pred_el = el
        self.pred_az_lbl.setText(str(round(self.pred_az,1)))
        self.pred_el_lbl.setText(str(round(self.pred_el,1)))
        if self.pred_conn_state == 2: #active connection
            if self.auto_track_cb.isChecked() == True: #auto track enables
                self.tar_az = round(self.pred_az, 1)
                self.tar_el = round(self.pred_el,1)
                self.update_target_azimuth()
                self.update_target_elevation()
                self.callback.set_position(self.tar_az, self.tar_el, True)

    def predict_callback_get(self):
        #function called by gpredict thread
        #gets current angles for gpredict feedback
        if self.pred_conn_state == 2:
            return self.cur_az, self.cur_el
        #self.update_predict_status()

    def predict_timeout(self):
        self.update_predict_status()

    def update_predict_status(self):
        if self.pred_conn_state == 0: #Disconnected
            self.predict_button.setText('Connect')
            self.pred_status_lbl.setText("Disconnected")
            self.pred_status_lbl.setStyleSheet("QLabel {  font-weight:bold; color:rgb(255,0,0) ; }")
            #self.gpredict_ip_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
            #self.gpredict_port_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
            self.gpredict_ip_le.setEnabled(True)
            self.gpredict_port_le.setEnabled(True)
        elif self.pred_conn_state == 1: #Listening
            self.predict_button.setText('Disconnect')
            self.pred_status_lbl.setText("Listening...")
            self.pred_status_lbl.setStyleSheet("QLabel {  font-weight:bold; color:rgb(255,255,0) ; }")
            #self.gpredict_ip_le.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
            #self.gpredict_port_le.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
            self.gpredict_ip_le.setEnabled(False)
            self.gpredict_port_le.setEnabled(False)
        elif self.pred_conn_state == 2: #Connected
            self.predict_button.setText('Disconnect')
            self.pred_status_lbl.setText("Connected")
            self.pred_status_lbl.setStyleSheet("QLabel {  font-weight:bold; color:rgb(0,255,0) ; }")
            #self.gpredict_ip_le.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
            #self.gpredict_port_le.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
            self.gpredict_ip_le.setEnabled(False)
            self.gpredict_port_le.setEnabled(False)
    #---- END GPREDICT and AUTO TRACK FUNCTIONS -----
        #self.parent.increment_target_angle(self.az_el,float(sender.text()))
