#!/usr/bin/env python3
#-- coding: utf-8 --
import datetime
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtCore import pyqtSignal

class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        # self.setContentsMargins(1,5,1,1)
        # self.setMinimumSize(50,50)
        self.init_widgets()
        # self.connect_signals()

    def update_status(self,msg):
        print(msg)

        self.ptu_conn_lbl.setText('Autostar: DISCONNECTED')
        self.adsb_conn_lbl.setText('ADSB')
        self.cur_azel_lbl.setText('XXX.XX / XX.XX')
        self.com_azel_lbl.setText('XXX.XX / XX.XX')
        self.tar_azel_lbl.setText('XXX.XX / XX.XX')
        self.tar_icao_lbl.setText('ICAO: ABCDEF')

    def update_icao(self, icao):
        self.tar_icao_lbl.setText('ICAO: {:s}'.format(icao))

    def update_current_angle(self, az, el):
        self.cur_azel_lbl.setText("{:3.2f} / {:2.2f}".format(az,el))

    def update_command_angle(self, az, el):
        self.com_azel_lbl.setText("{:3.2f} / {:2.2f}".format(az,el))

    def update_target_angle(self, az, el, rng):
        self.tar_azel_lbl.setText("{:3.2f} / {:2.2f} / {:3.1f}k".format(az,el,rng))

    def update_dev_conn_status(self,state):
        if state:
            # self.ptu_conn_lbl.setText('Autostar: CONNECTED')
            self.ptu_conn_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        elif not state:
            # self.ptu_conn_lbl.setText('Autostar: DISCONNECTED')
            self.ptu_conn_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")

    def update_sbs1_connection_state(self,state):
        if state:
            # self.ptu_conn_lbl.setText('Autostar: CONNECTED')
            self.adsb_conn_lbl.setStyleSheet("QLabel {font:10pt; font-weight:bold; color:rgb(0,255,0);}")
        elif not state:
            # self.ptu_conn_lbl.setText('Autostar: DISCONNECTED')
            self.adsb_conn_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")


    def init_widgets(self):
        lbl_width = 60
        val_width = 125
        lbl_height = 12
        btn_height = 20

        self.ptu_conn_lbl = Qt.QLabel()
        self.ptu_conn_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.ptu_conn_lbl.setText('AUTOSTAR')
        self.ptu_conn_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.ptu_conn_lbl.setFixedHeight(20)

        self.adsb_conn_lbl = Qt.QLabel()
        self.adsb_conn_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.adsb_conn_lbl.setText('ADSB')
        self.adsb_conn_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.adsb_conn_lbl.setFixedHeight(20)

        self.mlat_conn_lbl = Qt.QLabel()
        self.mlat_conn_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.mlat_conn_lbl.setText('MLAT')
        self.mlat_conn_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.mlat_conn_lbl.setFixedHeight(20)

        self.cur_azel_lbl = Qt.QLabel()
        self.cur_azel_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.cur_azel_lbl.setText('XXX.XX / XX.XX')
        self.cur_azel_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.cur_azel_lbl.setFixedHeight(20)

        self.com_azel_lbl = Qt.QLabel()
        self.com_azel_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.com_azel_lbl.setText('XXX.XX / XX.XX')
        self.com_azel_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(0,100,255);}")
        self.com_azel_lbl.setFixedHeight(20)

        self.tar_azel_lbl = Qt.QLabel()
        self.tar_azel_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.tar_azel_lbl.setText('XXX.XX / XX.XX')
        self.tar_azel_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tar_azel_lbl.setFixedHeight(20)

        self.tar_icao_lbl = Qt.QLabel()
        self.tar_icao_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.tar_icao_lbl.setText('ICAO: ABCDEF')
        self.tar_icao_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,255,0);}")
        self.tar_icao_lbl.setFixedHeight(20)

        self.addWidget(self.ptu_conn_lbl)
        self.addWidget(self.adsb_conn_lbl)
        self.addWidget(self.mlat_conn_lbl)
        self.addWidget(self.cur_azel_lbl)
        self.addWidget(self.com_azel_lbl)
        self.addWidget(self.tar_azel_lbl)
        self.addWidget(self.tar_icao_lbl)
