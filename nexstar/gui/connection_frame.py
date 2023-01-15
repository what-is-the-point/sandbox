#!/usr/bin/env python3
#-- coding: utf-8 --
import datetime
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal


class ConnectionFrameNet(Qt.QFrame):
    def __init__(self, cfg=None, parent=None):
        super(ConnectionFrameNet, self).__init__()
        self.cfg = cfg
        self.parent = parent
        self.setTitle(self.cfg['name'])
        self.setContentsMargins(1,1,1,1)
        self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.initUI()

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        self.setMinimumSize(100,100)
        self.init_widgets()
        #self.connect_signals()

    def init_widgets(self):
        lbl_width = 45
        val_width = 125
        lbl_height = 12

        self.ip_le = Qt.QLineEdit()
        self.ip_le.setText(self.cfg['ip'])
        self.ip_le.setInputMask("000.000.000.000;")
        self.ip_le.setEchoMode(Qt.QLineEdit.Normal)
        self.ip_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.ip_le.setMaxLength(15)
        self.ip_le.setFixedHeight(20)
        self.ip_le.setFixedWidth(125)

        self.port_le = Qt.QLineEdit()
        self.port_le.setText(str(self.cfg['port']))
        port_validator = Qt.QIntValidator()
        port_validator.setRange(0,65535)
        self.port_le.setValidator(port_validator)
        self.port_le.setEchoMode(Qt.QLineEdit.Normal)
        self.port_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.port_le.setMaxLength(5)
        self.port_le.setFixedWidth(50)
        self.port_le.setFixedHeight(20)

        conn_hbox = Qt.QHBoxLayout()
        conn_hbox.addWidget(self.ip_le)
        conn_hbox.addWidget(self.port_le)

        label = Qt.QLabel('Status:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {color:rgb(255,255,255);}")
        label.setFixedHeight(20)
        self.conn_status_lbl = Qt.QLabel('Disconnected')
        self.conn_status_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.conn_status_lbl.setStyleSheet("QLabel {font-weight:bold; color:rgb(255,0,0);}")
        self.conn_status_lbl.setFixedWidth(125)
        self.conn_status_lbl.setFixedHeight(20)

        stat_hbox = Qt.QHBoxLayout()
        stat_hbox.addWidget(label)
        stat_hbox.addWidget(self.conn_status_lbl)

        #Connection Button & Connection Status
        self.connect_button = Qt.QPushButton("Connect")
        # self.connect_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(255,0,0);}")
        self.connect_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(200,200,200);}")
        #self.connect_button.setStyleSheet("QPushButton {font:10pt;}")
        self.connect_button.setFixedHeight(20)
        self.connect_button.setFixedWidth(100)

        btn_hbox = Qt.QHBoxLayout()
        # btn_hbox.addStretch(1)
        btn_hbox.addWidget(self.connect_button)
        # btn_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        vbox.addLayout(conn_hbox)
        vbox.addLayout(stat_hbox)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)

class ConnectionFrameSerial(QGroupBox):
    connectFrameSignal = pyqtSignal(dict)
    def __init__(self, cfg, parent=None):
        super(ConnectionFrameSerial, self).__init__()
        self.cfg = cfg
        self.parent = parent
        self.setTitle(self.cfg['name'])
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255); margin-top: 5px}")
        self.setContentsMargins(1,1,1,1)
        self.port = cfg['port']
        self.baud = cfg['baud']
        self.connected = False
        self.initUI()


    def initUI(self):
        # self.setFrameShape(Qt.QFrame.StyledPanel)
        self.init_widgets()
        self.connect_signals()

    def connect_signals(self):
        self.port_le.editingFinished.connect(self._port_edit)
        # self.baud_le.editingFinished.connect(self._baud_edit)
        self.connect_button.clicked.connect(self._connect)

    def _port_edit(self):
        self.port = self.port_le.text()

    # def _baud_edit(self):
    #     self.baud = int(self.baud_le.text())

    def _connect(self):
        self.conn_status_lbl.setText('Connecting...')
        self.conn_status_lbl.setStyleSheet("QLabel {font:10pt; \
                                                    font-weight:bold; \
                                                    color:rgb(255,255,0);}")
        msg={
            "type":"autostar",
            "cmd":"connect",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "port": self.port,
                "baud": self.baud,
                "connect": (not self.connected)
            }
        }
        self.connectFrameSignal.emit(msg)
        # self.update_connection_state()

    def update_connection_state(self, state):
        # print(type(state), state)
        self.connected = state
        if self.connected == True:
            self.connect_button.setText('Disconnect')
            self.conn_status_lbl.setText('CONNECTED')
            self.conn_status_lbl.setStyleSheet("QLabel {font:10pt; \
                                                        font-weight:bold; \
                                                        color:rgb(0,255,0);}")
            #self.update_timer.start()
        elif self.connected == False:
            self.connect_button.setText('Connect')
            self.conn_status_lbl.setText('DISCONNECTED')
            self.conn_status_lbl.setStyleSheet("QLabel {font:10pt; \
                                                        font-weight:bold; \
                                                        color:rgb(255,0,0);}")
            #self.update_timer.stop()

    def init_widgets(self):
        lbl_width = 45
        val_width = 125
        lbl_height = 12

        #Device
        devLabel = Qt.QLabel("Device:")
        devLabel.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        devLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        devLabel.setFixedWidth(lbl_width)
        self.port_le = Qt.QLineEdit()
        self.port_le.setText(self.cfg['port'])
        self.port_le.setEchoMode(Qt.QLineEdit.Normal)
        self.port_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.port_le.setFixedWidth(val_width)
        self.port_le.setFixedHeight(20)

        dev_hbox = Qt.QHBoxLayout()
        dev_hbox.addWidget(devLabel)
        dev_hbox.addWidget(self.port_le)
        dev_hbox.addStretch(1)

        #Baud
        # baudLabel = Qt.QLabel("Baud:")
        # baudLabel.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        # baudLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        # baudLabel.setFixedWidth(lbl_width)
        #
        # self.baud_le = Qt.QLineEdit()
        # self.baud_le.setText(str(self.cfg['baud']))
        # port_validator = Qt.QIntValidator()
        # port_validator.setRange(0,65535)
        # self.baud_le.setValidator(port_validator)
        # self.baud_le.setEchoMode(Qt.QLineEdit.Normal)
        # self.baud_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        # self.baud_le.setMaxLength(5)
        # self.baud_le.setFixedWidth(val_width)
        # self.baud_le.setFixedHeight(20)
        #
        # baud_hbox = Qt.QHBoxLayout()
        # baud_hbox.addWidget(baudLabel)
        # baud_hbox.addWidget(self.baud_le)
        # baud_hbox.addStretch(1)

        #Connection Button & Connection Status
        self.connect_button = Qt.QPushButton("Connect")
        self.connect_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.connect_button.setFixedHeight(20)
        self.connect_button.setFixedWidth(100)

        btn_hbox = Qt.QHBoxLayout()
        # btn_hbox.addStretch(1)
        btn_hbox.addWidget(self.connect_button)
        btn_hbox.addStretch(1)

        status_lbl = Qt.QLabel('Status:')
        status_lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        status_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        status_lbl.setFixedHeight(lbl_height)
        status_lbl.setFixedWidth(lbl_width)
        self.conn_status_lbl = Qt.QLabel('Disconnected')
        self.conn_status_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.conn_status_lbl.setStyleSheet("QLabel {font:10pt; font-weight:bold; color:rgb(255,0,0);}")
        self.conn_status_lbl.setFixedWidth(val_width)
        self.conn_status_lbl.setFixedHeight(lbl_height)

        status_hbox = Qt.QHBoxLayout()
        status_hbox.addWidget(status_lbl)
        status_hbox.addWidget(self.conn_status_lbl)
        status_hbox.addStretch(1)


        vbox = Qt.QVBoxLayout()
        vbox.addLayout(dev_hbox)
        # vbox.addLayout(baud_hbox)
        vbox.setSpacing(2)
        vbox.addLayout(status_hbox)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)
