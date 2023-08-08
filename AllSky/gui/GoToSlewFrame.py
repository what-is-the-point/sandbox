#!/usr/bin/env python3
#-- coding: utf-8 --
import datetime
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal
import numpy as np

class GoToSlewFrame(QGroupBox):
    gotoSignal = pyqtSignal(dict)
    stopSignal = pyqtSignal(dict)
    querySignal = pyqtSignal(dict)
    def __init__(self, az=None, el=None, query_rate=1, parent=None):
        super(GoToSlewFrame, self).__init__()
        self.parent = parent
        self.cmd_az = az['home']
        self.cmd_el = el['home']
        self.trim_az = az['trim']
        self.trim_el = el['trim']
        self.az_auto_delta = az['auto_delta']
        self.el_auto_delta = el['auto_delta']

        self.query_rate = query_rate
        self._auto_track = False
        self._auto_update_com = False
        self.dev_connected = False

        self.cur_az = 0.0
        self.cur_el = 0.0
        self.com_az = 0.0
        self.com_el = 0.0
        self.tar_az = az['home']
        self.tar_el = el['home']
        self.tar_az_last = None
        self.tar_el_last = None
        self.az_delta = 0.0
        self.el_delta = 0.0
        self.az_rate = 0
        self.el_rate = 0
        self.home_az = az['home']
        self.home_el = el['home']
        self.setTitle("GoTo Slew / Autotrack")
        # self.setContentsMargins(1,5,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.setMinimumSize(200,100)
        self.initUI()

    def initUI(self):
        self.setMinimumSize(50, 50)
        self.init_widgets()
        self.init_timers()
        self.connect_signals()

    def init_timers(self):
        self.query_timer = QtCore.QTimer(self)
        self.query_timer.setInterval(1000)


    def connect_signals(self):
        self.stopButton.clicked.connect(self.stopButton_event)
        self.slewButton.clicked.connect(self.slewButton_event)

        self.azTextBox.editingFinished.connect(self._azimuth_edit)
        self.elTextBox.editingFinished.connect(self._elevation_edit)
        self.AzTrimSpinBox.valueChanged.connect(self._update_azimuth_trim)
        self.ElTrimSpinBox.valueChanged.connect(self._update_elevation_trim)

        self.query_cb.clicked.connect(self._query_cb_event)
        self.query_rate_le.editingFinished.connect(self._query_rate_edit)
        self.query_timer.timeout.connect(self.queryButton_event)

        self.update_com_cb.clicked.connect(self._update_com_cb_event)
        self.track_cb.clicked.connect(self._track_cb_event)

    def connect_signals_old(self):
        self.stopButton.clicked.connect(self.stopButton_event)
        self.slewButton.clicked.connect(self.slewButton_event)

        self.azTextBox.editingFinished.connect(self._azimuth_edit)
        self.elTextBox.editingFinished.connect(self._elevation_edit)
        self.query_rate_le.editingFinished.connect(self._query_rate_edit)
        self.AzTrimSpinBox.valueChanged.connect(self._update_azimuth_trim)
        self.ElTrimSpinBox.valueChanged.connect(self._update_elevation_trim)

        self.AzDeltaSpinBox.valueChanged.connect(self._update_azimuth_delta)
        self.ElDeltaSpinBox.valueChanged.connect(self._update_elevation_delta)

        self.query_cb.clicked.connect(self._query_cb_event)
        self.update_tar_cb.clicked.connect(self._update_tar_cb_event)
        self.track_cb.clicked.connect(self._track_cb_event)

        self.query_timer.timeout.connect(self.queryButton_event)

    def _update_azimuth_delta(self):
        self.az_delta = self.AzDeltaSpinBox.value()

    def _update_elevation_delta(self):
        self.el_delta = self.ElDeltaSpinBox.value()

    def _update_azimuth_trim(self):
        self.trim_az = self.AzTrimSpinBox.value()

    def _update_elevation_trim(self):
        self.trim_el = self.ElTrimSpinBox.value()

    def _query_cb_event(self):
        if self.query_cb.isChecked():
            self.query_timer.setInterval(int(self.query_rate*1000))
            self.query_timer.start()
        else:
            self.query_timer.stop()

    def _update_com_cb_event(self):
        self._auto_update_com = self.update_com_cb.isChecked()

    def _track_cb_event(self):
        self._auto_track = self.track_cb.isChecked()
        if self._auto_track:
            pass
        else:
            self.az_rate = 0
            self.el_rate = 0
            self.stopButton_event

    def _query_rate_edit(self):
        self.query_rate = float(self.query_rate_le.text())
        self.query_timer.setInterval(int(self.query_rate*1000))

    def _azimuth_edit(self):
        self.cmd_az = float(self.azTextBox.text())+ self.trim_az

    def _elevation_edit(self):
        self.cmd_el = float(self.elTextBox.text())+ self.trim_el


    def update_dev_conn_status(self,state):
        self.dev_connected = state
        print(state)

        if self.dev_connected:
            self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                         background-color:rgb(45,47,44); \
                                         color:rgb(255,0,0); }")
            self.track_cb.setEnabled(True)
            pass
        else:
            self.query_cb.setChecked(False)
            self.query_timer.stop()
            self.track_cb.setChecked(False)
            self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                         background-color:rgb(45,47,44); \
                                         color:rgb(200,200,200); }")
            self.track_cb.setEnabled(False)

    def update_current_angle(self,az,el):
        self.cur_az = az
        self.cur_el = el
        self.curAzLabel.setText("{:3.2f}".format(self.cur_az))
        self.curElLabel.setText("{:2.2f}".format(self.cur_el))

    def update_command_angle(self,az,el):
        self.com_az = az
        self.com_el = el
        self.comAzLabel.setText("{:3.2f}".format(self.com_az))
        self.comElLabel.setText("{:2.2f}".format(self.com_el))

    def update_target_angle(self,az,el):
        self.tar_az = az
        self.tar_el = el
        self.tarAzLabel.setText("{:3.2f}".format(self.tar_az))
        self.tarElLabel.setText("{:2.2f}".format(self.tar_el))

        self.az_delta = self.tar_az - self.cur_az
        self.el_delta = self.tar_el - self.cur_el
        if abs(self.az_delta) > 180.0:
            if  self.az_delta <= 0: self.az_delta += 360
            elif self.az_delta > 0: self.az_delta -= 360

        if abs(self.az_delta) >= self.az_auto_delta[0]:
            self.az_rate = 9
        elif (abs(self.az_delta) < self.az_auto_delta[0]) and (abs(self.az_delta) >= self.az_auto_delta[1]):
            self.az_rate = 8
        elif (abs(self.az_delta) < self.az_auto_delta[1]) and (abs(self.az_delta) >= self.az_auto_delta[2]):
            self.az_rate = 7
        elif (abs(self.az_delta) < self.az_auto_delta[2]) and (abs(self.az_delta) >= self.az_auto_delta[3]):
            self.az_rate = 6
        elif (abs(self.az_delta) < self.az_auto_delta[3]) and (abs(self.az_delta) >= self.az_auto_delta[4]):
            self.az_rate = 5
        elif (abs(self.az_delta) < self.az_auto_delta[4]) and (abs(self.az_delta) >= self.az_auto_delta[5]):
            self.az_rate = 4
        elif (abs(self.az_delta) < self.az_auto_delta[5]):
            self.az_rate = 3
        else:
            self.az_rate = 0

        # self.az_rate = int(abs(self.az_delta))
        if self.az_rate >9: self.az_rate = 9

        if abs(self.el_delta) >= self.el_auto_delta[0]:
            self.el_rate = 9
        elif (abs(self.el_delta) < self.el_auto_delta[0]) and (abs(self.el_delta) >= self.el_auto_delta[1]):
            self.el_rate = 8
        elif (abs(self.el_delta) < self.el_auto_delta[1]) and (abs(self.el_delta) >= self.el_auto_delta[2]):
            self.el_rate = 7
        elif (abs(self.el_delta) < self.el_auto_delta[2]) and (abs(self.el_delta) >= self.el_auto_delta[3]):
            self.el_rate = 6
        elif (abs(self.el_delta) < self.el_auto_delta[3]) and (abs(self.el_delta) >= self.el_auto_delta[4]):
            self.el_rate = 5
        elif (abs(self.el_delta) < self.el_auto_delta[4]) and (abs(self.el_delta) >= self.el_auto_delta[5]):
            self.el_rate = 4
        elif (abs(self.el_delta) < self.el_auto_delta[5]):
            self.el_rate = 3
        else:
            self.el_rate = 0
        # self.el_rate = int(abs(self.el_delta)/10)
        # if self.el_rate > 9: self.el_rate = 9
        # if self.el_rate < 3: self.el_rate = 3

        self.az_rate = int(self.az_rate * np.sign(self.az_delta))
        self.el_rate = int(self.el_rate * np.sign(self.el_delta))

        self.delAzLabel.setText("{:+3.1f}/{:+d}".format(self.az_delta, self.az_rate))
        self.delElLabel.setText("{:+2.1f}/{:+d}".format(self.el_delta, self.el_rate))

        if self._auto_update_com:
            self.azTextBox.setText("{:3.2f}".format(self.tar_az))
            self.elTextBox.setText("{:2.2f}".format(self.tar_el))
        if self._auto_track:
            self.slewButton_event()


    def update_target_angle_old(self,az,el):
        self.tar_az = az
        self.tar_el = el
        self.tarAzLabel.setText("{:3.2f}".format(self.tar_az))
        self.tarElLabel.setText("{:2.2f}".format(self.tar_el))

        if (self.tar_az_last == None) and (self.tar_el_last == None):
            self.tar_az_last = az
            self.tar_el_last = el
        else:
            d_az = abs(self.tar_az_last - self.tar_az)
            d_el = abs(self.tar_el_last - self.tar_el)
            self.DeltaLabel.setText("{:3.2f}/{:1.2f}".format(d_az, d_el))

        if self._auto_update:
            self.azTextBox.setText("{:3.2f}".format(az))
            self.elTextBox.setText("{:2.2f}".format(el))
        if self._auto_track:
            if (d_az > self.az_delta): self.tar_az_last = az
            if (d_el > self.el_delta): self.tar_el_last = el

            if (d_az > self.az_delta) or (d_el > self.el_delta):
                self.gotoButton_event()


    def slewButton_event(self):
        self.cmd_az = float(self.azTextBox.text()) + self.trim_az
        self.cmd_el = float(self.elTextBox.text()) + self.trim_el
        msg={
            "type":"nexstar",
            "cmd":"goto.slew",
            'src': 'gui.gotoslew',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "com_az": self.cmd_az,
                "com_el": self.cmd_el,
                "az_rate": self.az_rate,
                "el_rate": self.el_rate
            }
        }
        if self.dev_connected: self.gotoSignal.emit(msg)

    def stopButton_event(self):
        msg={
            "type":"nexstar",
            "cmd":"stop.slew",
            'src': 'gui.gotoslew',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        if self.dev_connected: self.stopSignal.emit(msg)

    def queryButton_event(self):
        msg={
            "type":"nexstar",
            "cmd":"position",
            'src': 'gui.gotoslew',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        if self.dev_connected: self.querySignal.emit(msg)


    def init_widgets(self):
        lbl_width = 20
        val_width = 45
        lbl_height = 12
        btn_height = 20

        lbl1 = Qt.QLabel("")
        lbl1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        lbl1.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl1.setFixedWidth(lbl_width)
        lbl1.setFixedHeight(lbl_height)
        lbl2 = Qt.QLabel("CUR")
        lbl2.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        lbl2.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl2.setFixedWidth(val_width)
        lbl2.setFixedHeight(lbl_height)
        lbl3 = Qt.QLabel("COM")
        lbl3.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        lbl3.setStyleSheet("QLabel {font:10pt; color:rgb(0,100,255);}")
        lbl3.setFixedWidth(val_width)
        lbl3.setFixedHeight(lbl_height)
        lbl4 = Qt.QLabel("TAR")
        lbl4.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        lbl4.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        lbl4.setFixedWidth(val_width)
        lbl4.setFixedHeight(lbl_height)
        lbl5 = Qt.QLabel("DEL")
        lbl5.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        lbl5.setStyleSheet("QLabel {font:10pt; color:rgb(255,255,0);}")
        lbl5.setFixedWidth(val_width)
        lbl5.setFixedHeight(lbl_height)
        hdr_hbox = Qt.QHBoxLayout()
        hdr_hbox.addWidget(lbl1)
        hdr_hbox.addWidget(lbl2)
        hdr_hbox.addWidget(lbl3)
        hdr_hbox.addWidget(lbl4)
        hdr_hbox.addWidget(lbl5)

        label = Qt.QLabel("Az: ")
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedWidth(lbl_width)
        label.setFixedHeight(lbl_height)
        self.curAzLabel = Qt.QLabel("{:03.2f}".format(self.tar_az))
        self.curAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.curAzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.curAzLabel.setFixedWidth(val_width)
        self.curAzLabel.setFixedHeight(lbl_height)
        self.comAzLabel = Qt.QLabel("{:03.2f}".format(self.tar_az))
        self.comAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.comAzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,100,255);}")
        self.comAzLabel.setFixedWidth(val_width)
        self.comAzLabel.setFixedHeight(lbl_height)
        self.tarAzLabel = Qt.QLabel("{:03.2f}".format(self.tar_az))
        self.tarAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tarAzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tarAzLabel.setFixedWidth(val_width)
        self.tarAzLabel.setFixedHeight(lbl_height)
        self.delAzLabel = Qt.QLabel("{:+03.2f}".format(self.tar_az))
        self.delAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.delAzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,255,0);}")
        self.delAzLabel.setFixedWidth(val_width+10)
        self.delAzLabel.setFixedHeight(lbl_height)
        az_lbl_hbox = Qt.QHBoxLayout()
        az_lbl_hbox.addWidget(label)
        az_lbl_hbox.addWidget(self.curAzLabel)
        az_lbl_hbox.addWidget(self.comAzLabel)
        az_lbl_hbox.addWidget(self.tarAzLabel)
        az_lbl_hbox.addWidget(self.delAzLabel)
        # az_lbl_hbox.addStretch(1)

        label = Qt.QLabel("El: ")
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedWidth(lbl_width)
        label.setFixedHeight(lbl_height)
        self.curElLabel = Qt.QLabel("{:03.2f}".format(self.tar_el))
        self.curElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.curElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.curElLabel.setFixedWidth(val_width)
        self.curElLabel.setFixedHeight(lbl_height)
        self.comElLabel = Qt.QLabel("{:03.2f}".format(self.tar_el))
        self.comElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.comElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,100,255);}")
        self.comElLabel.setFixedWidth(val_width)
        self.comElLabel.setFixedHeight(lbl_height)
        self.tarElLabel = Qt.QLabel("{:02.2f}".format(self.tar_el))
        self.tarElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tarElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tarElLabel.setFixedWidth(val_width)
        self.tarElLabel.setFixedHeight(lbl_height)
        self.delElLabel = Qt.QLabel("{:+03.2f}".format(self.tar_el))
        self.delElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.delElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,255,0);}")
        self.delElLabel.setFixedWidth(val_width+10)
        self.delElLabel.setFixedHeight(lbl_height)
        el_lbl_hbox = Qt.QHBoxLayout()
        el_lbl_hbox.addWidget(label)
        el_lbl_hbox.addWidget(self.curElLabel)
        el_lbl_hbox.addWidget(self.comElLabel)
        el_lbl_hbox.addWidget(self.tarElLabel)
        el_lbl_hbox.addWidget(self.delElLabel)
        # el_lbl_hbox.addStretch(1)

        self.slewButton = Qt.QPushButton("Slew")
        self.slewButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.slewButton.setFixedHeight(20)
        self.stopButton = Qt.QPushButton("Stop")
        self.stopButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.stopButton.setFixedHeight(20)


        label = Qt.QLabel("Az:")
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(0,100,255);}")
        label.setFixedWidth(lbl_width)
        label.setFixedHeight(btn_height)
        self.azTextBox = Qt.QLineEdit()
        self.azTextBox.setText("{:3.2f}".format(self.cmd_az))
        self.azTextBox.setInputMask("#00.00;")
        self.azTextBox.setEchoMode(Qt.QLineEdit.Normal)
        # self.azTextBox.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.azTextBox.setStyleSheet("QLineEdit {font:10pt; \
                                                 background-color:rgb(0,100,255); \
                                                 color:rgb(0,0,0);}")
        self.azTextBox.setMaxLength(3)
        # self.azTextBox.setFixedWidth(val_width)
        self.azTextBox.setFixedHeight(btn_height)
        self.AzTrimSpinBox = Qt.QDoubleSpinBox()
        self.AzTrimSpinBox.setFixedHeight(20)
        self.AzTrimSpinBox.setRange(-3.0, 3.0)
        self.AzTrimSpinBox.setSingleStep(0.1)
        self.AzTrimSpinBox.setValue(self.trim_az)
        # self.AzTrimSpinBox.setSuffix('deg')
        self.AzTrimSpinBox.setStyleSheet("QDoubleSpinBox {font:10pt; \
                                                          background-color:rgb(0,100,255); \
                                                          color:rgb(0,0,0);}")

        az_hbox = Qt.QHBoxLayout()
        az_hbox.addWidget(label)
        # az_hbox.addStretch(1)
        az_hbox.addWidget(self.azTextBox)
        az_hbox.addWidget(self.AzTrimSpinBox)
        az_hbox.addWidget(self.slewButton)
        # az_hbox.addStretch(1)


        label = Qt.QLabel("El:")
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(0,100,255);}")
        label.setFixedWidth(lbl_width)
        label.setFixedHeight(20)
        self.elTextBox = Qt.QLineEdit()
        self.elTextBox.setText("{:2.2f}".format(self.cmd_el))
        self.elTextBox.setInputMask("#00.00;")
        self.elTextBox.setEchoMode(Qt.QLineEdit.Normal)
        # self.elTextBox.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.elTextBox.setStyleSheet("QLineEdit {font:10pt; \
                                                 background-color:rgb(0,100,255); \
                                                 color:rgb(0,0,0);}")
        self.elTextBox.setMaxLength(3)
        # self.elTextBox.setFixedWidth(val_width)
        self.elTextBox.setFixedHeight(20)
        self.ElTrimSpinBox = Qt.QDoubleSpinBox()
        self.ElTrimSpinBox.setFixedHeight(20)
        self.ElTrimSpinBox.setRange(-3.0, 3.0)
        self.ElTrimSpinBox.setSingleStep(0.1)
        self.ElTrimSpinBox.setValue(self.trim_el)
        self.ElTrimSpinBox.setStyleSheet("QDoubleSpinBox {font:10pt; \
                                                          background-color:rgb(0,100,255); \
                                                          color:rgb(0,0,0);}")
        el_hbox = Qt.QHBoxLayout()
        el_hbox.addWidget(label)
        # el_hbox.addStretch(1)
        el_hbox.addWidget(self.elTextBox)
        el_hbox.addWidget(self.ElTrimSpinBox)
        el_hbox.addWidget(self.stopButton)

        self.query_cb = Qt.QCheckBox("Auto Query [s]:")
        self.query_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(255,0,0); }")
        self.query_cb.setChecked(False)
        self.query_cb.setFixedWidth(110)
        self.query_cb.setFixedHeight(15)
        self.query_rate_le = Qt.QLineEdit()
        self.query_rate_le.setText("{:1.3f}".format(self.query_rate))
        self.query_val = Qt.QDoubleValidator()
        self.query_rate_le.setValidator(self.query_val)
        self.query_rate_le.setEchoMode(Qt.QLineEdit.Normal)
        self.query_rate_le.setStyleSheet("QLineEdit {font:10pt; \
                                          background-color:rgb(200,75,75); \
                                          color:rgb(0,0,0);}")
        self.query_rate_le.setMaxLength(4)
        self.query_rate_le.setFixedWidth(40)
        self.query_rate_le.setFixedHeight(15)
        query_hbox = Qt.QHBoxLayout()
        query_hbox.addWidget(self.query_cb)
        query_hbox.addWidget(self.query_rate_le)
        query_hbox.addStretch(1)

        self.update_com_cb = Qt.QCheckBox("Auto Update Commanded")
        self.update_com_cb.setStyleSheet("QCheckBox {font:10pt; \
                                          background-color:rgb(45,47,44); \
                                          color:rgb(255,0,0); }")
        self.update_com_cb.setChecked(False)
        self.update_com_cb.setFixedWidth(175)
        self.update_com_cb.setFixedHeight(15)
        self.update_com_cb.setEnabled(True)
        update_com_hbox = Qt.QHBoxLayout()
        update_com_hbox.addWidget(self.update_com_cb)
        update_com_hbox.addStretch(1)

        self.track_cb = Qt.QCheckBox("Auto Track Target")
        self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(200,200,200); }")
        self.track_cb.setChecked(False)
        self.track_cb.setFixedWidth(150)
        self.track_cb.setFixedHeight(15)
        self.track_cb.setEnabled(False)

        track_hbox = Qt.QHBoxLayout()
        track_hbox.addWidget(self.track_cb)
        track_hbox.addStretch(1)


        vbox = Qt.QVBoxLayout()
        vbox.setSpacing(2)
        vbox.addLayout(hdr_hbox)
        vbox.addLayout(az_lbl_hbox)
        vbox.addLayout(el_lbl_hbox)
        vbox.addLayout(az_hbox)
        vbox.addLayout(el_hbox)
        vbox.addLayout(query_hbox)
        vbox.addLayout(update_com_hbox)
        vbox.addLayout(track_hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def init_widgets_old(self):
        lbl_width = 60
        val_width = 50
        lbl_height = 12
        btn_height = 20

        label = Qt.QLabel("Azimuth:")
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedWidth(lbl_width)
        label.setFixedHeight(20)
        self.azTextBox = Qt.QLineEdit()
        self.azTextBox.setText("{:3.2f}".format(self.cmd_az))
        self.azTextBox.setInputMask("#00.00;")
        self.azTextBox.setEchoMode(Qt.QLineEdit.Normal)
        self.azTextBox.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.azTextBox.setMaxLength(3)
        self.azTextBox.setFixedWidth(val_width)
        self.azTextBox.setFixedHeight(20)
        self.tarAzLabel = Qt.QLabel("{:3.2f}".format(self.tar_az))
        self.tarAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tarAzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tarAzLabel.setFixedWidth(40)
        self.tarAzLabel.setFixedHeight(20)
        self.AzTrimSpinBox = Qt.QDoubleSpinBox()
        self.AzTrimSpinBox.setFixedHeight(20)
        self.AzTrimSpinBox.setRange(-3.0, 3.0)
        self.AzTrimSpinBox.setSingleStep(0.1)
        self.AzTrimSpinBox.setValue(self.trim_az)
        # self.AzTrimSpinBox.setSuffix('deg')
        self.AzTrimSpinBox.setStyleSheet("QDoubleSpinBox {font:10pt; \
                                                          background-color:rgb(200,75,75); \
                                                          color:rgb(0,0,0);}")
        az_hbox = Qt.QHBoxLayout()
        az_hbox.addWidget(label)
        az_hbox.addWidget(self.azTextBox)
        az_hbox.addWidget(self.AzTrimSpinBox)
        az_hbox.addWidget(self.tarAzLabel)
        az_hbox.addStretch(1)

        label = Qt.QLabel("Elevation:")
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedWidth(lbl_width)
        label.setFixedHeight(20)
        self.elTextBox = Qt.QLineEdit()
        # self.elTextBox.setText("00.000")
        self.elTextBox.setText("{:2.2f}".format(self.cmd_el))
        self.elTextBox.setInputMask("#00.00;")
        self.elTextBox.setEchoMode(Qt.QLineEdit.Normal)
        self.elTextBox.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.elTextBox.setMaxLength(3)
        self.elTextBox.setFixedWidth(val_width)
        self.elTextBox.setFixedHeight(20)
        self.tarElLabel = Qt.QLabel("{:2.2f}".format(self.tar_el))
        self.tarElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tarElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tarElLabel.setFixedWidth(40)
        self.tarElLabel.setFixedHeight(20)
        self.ElTrimSpinBox = Qt.QDoubleSpinBox()
        self.ElTrimSpinBox.setFixedHeight(20)
        self.ElTrimSpinBox.setRange(-3.0, 3.0)
        self.ElTrimSpinBox.setSingleStep(0.1)
        self.ElTrimSpinBox.setValue(self.trim_el)
        self.ElTrimSpinBox.setStyleSheet("QDoubleSpinBox {font:10pt; \
                                                          background-color:rgb(200,75,75); \
                                                          color:rgb(0,0,0);}")
        el_hbox = Qt.QHBoxLayout()
        el_hbox.addWidget(label)
        el_hbox.addWidget(self.elTextBox)
        el_hbox.addWidget(self.ElTrimSpinBox)
        el_hbox.addWidget(self.tarElLabel)
        el_hbox.addStretch(1)

        self.query_cb = Qt.QCheckBox("Auto Query [s]:")
        self.query_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(255,0,0); }")
        self.query_cb.setChecked(False)
        self.query_cb.setFixedWidth(110)
        self.query_rate_le = Qt.QLineEdit()
        self.query_rate_le.setText("{:1.3f}".format(self.query_rate))
        self.query_val = Qt.QDoubleValidator()
        self.query_rate_le.setValidator(self.query_val)
        self.query_rate_le.setEchoMode(Qt.QLineEdit.Normal)
        self.query_rate_le.setStyleSheet("QLineEdit {font:10pt; \
                                          background-color:rgb(200,75,75); \
                                          color:rgb(0,0,0);}")
        self.query_rate_le.setMaxLength(4)
        self.query_rate_le.setFixedWidth(40)
        self.query_rate_le.setFixedHeight(20)
        query_hbox = Qt.QHBoxLayout()
        query_hbox.addWidget(self.query_cb)
        query_hbox.addWidget(self.query_rate_le)
        query_hbox.addStretch(1)

        self.update_tar_cb = Qt.QCheckBox("Auto Update Target")
        self.update_tar_cb.setStyleSheet("QCheckBox {font:10pt; \
                                          background-color:rgb(45,47,44); \
                                          color:rgb(255,0,0); }")
        self.update_tar_cb.setChecked(False)
        self.update_tar_cb.setFixedWidth(150)
        self.update_tar_cb.setEnabled(True)
        update_hbox = Qt.QHBoxLayout()
        update_hbox.addWidget(self.update_tar_cb)
        update_hbox.addStretch(1)

        self.track_cb = Qt.QCheckBox("Auto Track Target")
        self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(200,200,200); }")
        self.track_cb.setChecked(False)
        self.track_cb.setFixedWidth(150)
        self.track_cb.setEnabled(False)

        track_hbox = Qt.QHBoxLayout()
        track_hbox.addWidget(self.track_cb)
        track_hbox.addStretch(1)


        AzLabel = Qt.QLabel("dAz:")
        AzLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        AzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        AzLabel.setFixedWidth(25)
        AzLabel.setFixedHeight(20)
        self.AzDeltaSpinBox = Qt.QDoubleSpinBox()
        self.AzDeltaSpinBox.setFixedHeight(20)
        self.AzDeltaSpinBox.setRange(0, 2.0)
        self.AzDeltaSpinBox.setSingleStep(0.1)
        self.AzDeltaSpinBox.setValue(self.az_delta)
        self.AzDeltaSpinBox.setStyleSheet("QDoubleSpinBox {font:10pt; \
                                                          background-color:rgb(200,75,75); \
                                                          color:rgb(0,0,0);}")
        ElLabel = Qt.QLabel("dEl:")
        ElLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        ElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        ElLabel.setFixedWidth(25)
        ElLabel.setFixedHeight(20)
        self.ElDeltaSpinBox = Qt.QDoubleSpinBox()
        self.ElDeltaSpinBox.setFixedHeight(20)
        self.ElDeltaSpinBox.setRange(0, 2.0)
        self.ElDeltaSpinBox.setSingleStep(0.1)
        self.ElDeltaSpinBox.setValue(self.el_delta)
        self.ElDeltaSpinBox.setStyleSheet("QDoubleSpinBox {font:10pt; \
                                                          background-color:rgb(200,75,75); \
                                                          color:rgb(0,0,0);}")

        self.DeltaLabel = Qt.QLabel("X.XX / X.XX")
        self.DeltaLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.DeltaLabel.setStyleSheet("QLabel {font:8pt; color:rgb(0,255,0);}")
        self.DeltaLabel.setFixedWidth(60)
        self.DeltaLabel.setFixedHeight(20)

        delta_hbox = Qt.QHBoxLayout()
        delta_hbox.addWidget(AzLabel)
        delta_hbox.addWidget(self.AzDeltaSpinBox)
        delta_hbox.addWidget(ElLabel)
        delta_hbox.addWidget(self.ElDeltaSpinBox)
        delta_hbox.addWidget(self.DeltaLabel)
        delta_hbox.addStretch(1)

        self.slewButton = Qt.QPushButton("Slew")
        self.slewButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.slewButton.setFixedHeight(20)
        self.stopButton = Qt.QPushButton("Stop")
        self.stopButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.stopButton.setFixedHeight(20)

        btn_hbox = Qt.QHBoxLayout()
        btn_hbox.addWidget(self.slewButton)
        # btn_hbox.addWidget(self.stopButton)
        btn_hbox.addWidget(self.stopButton)

        vbox1 = Qt.QVBoxLayout()
        vbox1.setSpacing(1)
        vbox1.addLayout(az_hbox)
        vbox1.addLayout(el_hbox)
        # vbox1.addLayout(btn_hbox)
        # vbox1.addLayout(query_hbox)
        vbox1.addLayout(update_hbox)
        vbox1.addLayout(track_hbox)
        vbox1.addLayout(delta_hbox)
        vbox1.addStretch(1)

        # vbox2 = Qt.QVBoxLayout()
        # vbox2.setSpacing(1)
        # vbox2.addLayout(query_hbox)
        # vbox2.addLayout(update_hbox)
        # vbox2.addLayout(track_hbox)
        # vbox2.addLayout(delta_hbox)
        # vbox2.addStretch(1)

        hbox = Qt.QHBoxLayout()
        hbox.addLayout(vbox1)
        # hbox.addLayout(vbox2)

        self.setLayout(hbox)
