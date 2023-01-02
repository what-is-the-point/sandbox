#!/usr/bin/env python3
#-- coding: utf-8 --
import datetime
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal

class GoToFrame(QGroupBox):
    gotoSignal = pyqtSignal(dict)
    stopSignal = pyqtSignal(dict)
    querySignal = pyqtSignal(dict)
    def __init__(self, az=0.0, el=0.0, query_rate=1, parent=None):
        super(GoToFrame, self).__init__()
        self.parent = parent
        self.cmd_az = az
        self.cmd_el = el
        self.tar_az = az
        self.tar_el = el
        self.query_rate = query_rate
        self._auto_track = False
        self.dev_connected = False
        self.setTitle("Go To Control")
        self.setContentsMargins(1,5,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.setMinimumSize(200,100)
        self.initUI()

    def initUI(self):
        # self.setFrameShape(Qt.QFrame.StyledPanel)
        self.setMinimumSize(50, 50)
        # self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.init_widgets()
        self.init_timers()
        self.connect_signals()

    def init_timers(self):
        self.query_timer = QtCore.QTimer(self)
        self.query_timer.setInterval(1000)


    def connect_signals(self):
        self.stopButton.clicked.connect(self.stopButton_event)
        self.gotoButton.clicked.connect(self.gotoButton_event)
        self.queryButton.clicked.connect(self.queryButton_event)
        self.azTextBox.editingFinished.connect(self._azimuth_edit)
        self.elTextBox.editingFinished.connect(self._elevation_edit)
        self.query_rate_le.editingFinished.connect(self._query_rate_edit)

        self.query_cb.clicked.connect(self._query_cb_event)
        self.track_cb.clicked.connect(self._track_cb_event)

        self.query_timer.timeout.connect(self.queryButton_event)

    def _query_cb_event(self):
        if self.query_cb.isChecked():
            self.query_timer.setInterval(int(self.query_rate*1000))
            self.query_timer.start()
        else:
            self.query_timer.stop()

    def _track_cb_event(self):
        self._auto_track = self.track_cb.isChecked()

    def _query_rate_edit(self):
        self.query_rate = float(self.query_rate_le.text())
        self.query_timer.setInterval(int(self.query_rate*1000))

    def _azimuth_edit(self):
        self.cmd_az = float(self.azTextBox.text())

    def _elevation_edit(self):
        self.cmd_el = float(self.elTextBox.text())

    def update_dev_conn_status(self,state):
        self.dev_connected = state
        if self.dev_connected:
            self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                         background-color:rgb(45,47,44); \
                                         color:rgb(255,0,0); }")
            self.track_cb.setEnabled(True)
        else:
            self.query_cb.setChecked(False)
            self.query_timer.stop()
            self.track_cb.setChecked(False)
            self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                         background-color:rgb(45,47,44); \
                                         color:rgb(200,200,200); }")
            self.track_cb.setEnabled(False)


    def update_target_angle(self,az,el):
        self.tarAzLabel.setText("{:3.2f}".format(az))
        self.tarElLabel.setText("{:2.2f}".format(el))
        if self._auto_track:
            self.cmd_az = az
            self.cmd_el = el
            self.azTextBox.setText("{:3.2f}".format(self.cmd_az))
            self.elTextBox.setText("{:2.2f}".format(self.cmd_el))
            # self.gotoButton_event()

    def gotoButton_event(self):
        self.cmd_az = float(self.azTextBox.text())
        self.cmd_el = float(self.elTextBox.text())
        msg={
            "type":"autostar",
            "cmd":"goto",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "azimuth": self.cmd_az,
                "elevation": self.cmd_el
            }
        }
        if self.dev_connected: self.gotoSignal.emit(msg)

    def stopButton_event(self):
        msg={
            "type":"autostar",
            "cmd":"stop",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        if self.dev_connected: self.stopSignal.emit(msg)

    def queryButton_event(self):
        msg={
            "type":"autostar",
            "cmd":"position",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        if self.dev_connected: self.querySignal.emit(msg)


    def init_widgets(self):
        lbl_width = 60
        val_width = 125
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
        self.azTextBox.setFixedWidth(80)
        self.azTextBox.setFixedHeight(20)
        self.tarAzLabel = Qt.QLabel("{:3.2f}".format(self.tar_az))
        self.tarAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tarAzLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tarAzLabel.setFixedWidth(50)
        self.tarAzLabel.setFixedHeight(20)
        az_hbox = Qt.QHBoxLayout()
        az_hbox.addWidget(label)
        az_hbox.addWidget(self.azTextBox)
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
        self.elTextBox.setFixedWidth(80)
        self.elTextBox.setFixedHeight(20)
        self.tarElLabel = Qt.QLabel("{:2.2f}".format(self.tar_el))
        self.tarElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tarElLabel.setStyleSheet("QLabel {font:10pt; color:rgb(0,255,0);}")
        self.tarElLabel.setFixedWidth(50)
        self.tarElLabel.setFixedHeight(20)
        el_hbox = Qt.QHBoxLayout()
        el_hbox.addWidget(label)
        el_hbox.addWidget(self.elTextBox)
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
        self.query_rate_le.setFixedWidth(50)
        self.query_rate_le.setFixedHeight(20)
        query_hbox = Qt.QHBoxLayout()
        query_hbox.addWidget(self.query_cb)
        query_hbox.addWidget(self.query_rate_le)
        query_hbox.addStretch(1)

        self.track_cb = Qt.QCheckBox("Auto Track")
        self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(200,200,200); }")
        self.track_cb.setChecked(False)
        self.track_cb.setFixedWidth(110)
        self.track_cb.setEnabled(False)
        track_hbox = Qt.QHBoxLayout()
        track_hbox.addWidget(self.track_cb)
        # track_hbox.addWidget(self.track_rate_le)
        track_hbox.addStretch(1)


        self.gotoButton = Qt.QPushButton("GoTo")
        self.gotoButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.gotoButton.setFixedHeight(20)
        self.stopButton = Qt.QPushButton("STOP")
        self.stopButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.stopButton.setFixedHeight(20)
        self.queryButton = Qt.QPushButton("Query")
        self.queryButton.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.queryButton.setFixedHeight(20)
        btn_hbox = Qt.QHBoxLayout()
        btn_hbox.addWidget(self.gotoButton)
        btn_hbox.addWidget(self.stopButton)
        btn_hbox.addWidget(self.queryButton)

        vbox1 = Qt.QVBoxLayout()
        vbox1.setSpacing(3)
        vbox1.addLayout(az_hbox)
        vbox1.addLayout(el_hbox)
        vbox1.addLayout(btn_hbox)
        vbox1.addStretch(1)

        vbox2 = Qt.QVBoxLayout()
        vbox2.setSpacing(3)
        vbox2.addLayout(query_hbox)
        vbox2.addLayout(track_hbox)
        vbox2.addStretch(1)

        hbox = Qt.QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)

        self.setLayout(hbox)
