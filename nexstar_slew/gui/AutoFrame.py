#!/usr/bin/env python3
#-- coding: utf-8 --
import datetime
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal

class AutoFrame(QGroupBox):
    autoQuerySignal = pyqtSignal(dict)
    autoTrackSignal = pyqtSignal(dict)
    def __init__(self, name="Auto Control", qr=0.25, tr=0.25, parent=None):
        super(AutoFrame, self).__init__()
        self.parent = parent
        self.query_rate = qr
        self.track_rate = tr
        self.setTitle(name)
        self.initUI()

    def initUI(self):
        self.setContentsMargins(1,5,1,1)
        self.setMinimumSize(50,50)
        self.init_widgets()
        self.connect_signals()

    def connect_signals(self):
        self.query_cb.clicked.connect(self.query_cb_event)
        self.track_cb.clicked.connect(self.track_cb_event)
        self.query_rate_le.editingFinished.connect(self._query_rate_edit)
        self.track_rate_le.editingFinished.connect(self._track_rate_edit)

    def _query_rate_edit(self):
        self.query_rate = float(self.query_rate_le.text())

    def _track_rate_edit(self):
        self.track_rate = float(self.track_rate_le.text())

    def query_cb_event(self):
        print(self.sender())
        msg={
            "type":"CTL",
            "cmd":"STOP",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        self.autoQuerySignal.emit(msg)

    def track_cb_event(self):
        msg={
            "type":"CTL",
            "cmd":"QUERY",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        self.autoTrackSignal.emit(msg)




    def init_widgets(self):
        lbl_width = 60
        val_width = 125
        lbl_height = 12
        btn_height = 20

        self.query_cb = Qt.QCheckBox("Auto Query [s]:")
        self.query_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(255,0,0); }")
        self.query_cb.setChecked(False)
        self.query_cb.setFixedWidth(110)
        self.query_rate_le = Qt.QLineEdit()
        self.query_rate_le.setText("0.25")
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

        self.track_cb = Qt.QCheckBox("Auto Track [s]:")
        self.track_cb.setStyleSheet("QCheckBox {font:10pt; \
                                     background-color:rgb(45,47,44); \
                                     color:rgb(255,0,0); }")
        self.track_cb.setChecked(False)
        self.track_cb.setFixedWidth(110)
        self.track_rate_le = Qt.QLineEdit()
        self.track_rate_le.setText("0.25")
        self.query_val = Qt.QDoubleValidator()
        self.track_rate_le.setValidator(self.query_val)
        self.track_rate_le.setEchoMode(Qt.QLineEdit.Normal)
        self.track_rate_le.setStyleSheet("QLineEdit {font:10pt; \
                                          background-color:rgb(200,75,75); \
                                          color:rgb(0,0,0);}")
        self.track_rate_le.setMaxLength(4)
        self.track_rate_le.setFixedWidth(50)
        self.track_rate_le.setFixedHeight(20)
        track_hbox = Qt.QHBoxLayout()
        track_hbox.addWidget(self.track_cb)
        track_hbox.addWidget(self.track_rate_le)
        track_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        vbox.setSpacing(3)
        vbox.addLayout(query_hbox)
        vbox.addLayout(track_hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)
