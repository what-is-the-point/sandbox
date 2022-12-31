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
    def __init__(self, az=0.0, el=0.0, auto_rate=1, parent=None):
        super(GoToFrame, self).__init__()
        self.parent = parent
        self.cmd_az = az
        self.cmd_el = el
        self.tar_az = az
        self.tar_el = el
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
        self.connect_signals()

    def connect_signals(self):
        self.stopButton.clicked.connect(self.stopButton_event)
        self.gotoButton.clicked.connect(self.gotoButton_event)
        self.queryButton.clicked.connect(self.queryButton_event)
        self.azTextBox.editingFinished.connect(self._azimuth_edit)
        self.elTextBox.editingFinished.connect(self._elevation_edit)

    def _azimuth_edit(self):
        self.cmd_az = float(self.azTextBox.text())

    def _elevation_edit(self):
        self.cmd_el = float(self.elTextBox.text())

    def update_target_angle(self,az,el):
        self.tarAzLabel.setText("{:3.2f}".format(az))
        self.tarElLabel.setText("{:2.2f}".format(el))

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
        self.gotoSignal.emit(msg)

    def stopButton_event(self):
        msg={
            "type":"autostar",
            "cmd":"stop",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        self.stopSignal.emit(msg)

    def queryButton_event(self):
        msg={
            "type":"autostar",
            "cmd":"position",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        self.querySignal.emit(msg)


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

        # self.auto_query_cb = Qt.QCheckBox("Auto Query [s]:")
        # self.auto_query_cb.setStyleSheet("QCheckBox {font:10pt; \
        #                                   background-color:rgb(45,47,44); \
        #                                   color:rgb(255,0,0); }")
        # self.auto_query_cb.setChecked(True)
        # self.auto_query_cb.setFixedWidth(110)
        # self.fb_query_rate_le = Qt.QLineEdit()
        # self.fb_query_rate_le.setText("0.25")
        # self.query_val = Qt.QDoubleValidator()
        # self.fb_query_rate_le.setValidator(self.query_val)
        # self.fb_query_rate_le.setEchoMode(Qt.QLineEdit.Normal)
        # self.fb_query_rate_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        # self.fb_query_rate_le.setMaxLength(4)
        # self.fb_query_rate_le.setFixedWidth(50)
        # self.fb_query_rate_le.setFixedHeight(20)
        # auto_query_hbox = Qt.QHBoxLayout()
        # auto_query_hbox.addWidget(self.auto_query_cb)
        # auto_query_hbox.addWidget(self.fb_query_rate_le)
        # auto_query_hbox.addStretch(1)
        #
        # self.auto_track_cb = Qt.QCheckBox("Auto Track [s]:")
        # self.auto_track_cb.setStyleSheet("QCheckBox {font:10pt; \
        #                                   background-color:rgb(45,47,44); \
        #                                   color:rgb(255,0,0); }")
        # self.auto_track_cb.setChecked(True)
        # self.auto_track_cb.setFixedWidth(110)
        # self.at_query_rate_le = Qt.QLineEdit()
        # self.at_query_rate_le.setText("0.25")
        # self.query_val = Qt.QDoubleValidator()
        # self.at_query_rate_le.setValidator(self.query_val)
        # self.at_query_rate_le.setEchoMode(Qt.QLineEdit.Normal)
        # self.at_query_rate_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        # self.at_query_rate_le.setMaxLength(4)
        # self.at_query_rate_le.setFixedWidth(50)
        # self.at_query_rate_le.setFixedHeight(20)
        # auto_track_hbox = Qt.QHBoxLayout()
        # auto_track_hbox.addWidget(self.auto_track_cb)
        # auto_track_hbox.addWidget(self.at_query_rate_le)
        # auto_track_hbox.addStretch(1)

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

        vbox = Qt.QVBoxLayout()
        vbox.setSpacing(3)
        vbox.addLayout(az_hbox)
        vbox.addLayout(el_hbox)
        # vbox.addLayout(auto_query_hbox)
        # vbox.addLayout(auto_track_hbox)
        vbox.addLayout(btn_hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)
