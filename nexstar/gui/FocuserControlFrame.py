#!/usr/bin/env python3
#version 2.1

from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal
import datetime

class FocuserControlFrame(QGroupBox):
    focusSignal = pyqtSignal(dict)
    def __init__(self, cfg=None, parent=None):
        super(FocuserControlFrame, self).__init__()
        self.parent = parent
        self.setTitle(cfg['name'])
        self.setContentsMargins(1,10,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.setMinimumSize(50, 50)
        self.initUI()

    def initUI(self):
        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        self.FastMinusButton = Qt.QPushButton(self)
        self.FastMinusButton.setText("<< -")
        self.FastMinusButton.setMinimumWidth(35)
        # self.FastMinusButton.setFixedHeight(20)
        self.FastMinusButton.setStyleSheet("QPushButton {font:12pt; font-weight: bold; \
                                                         background-color:rgb(220,0,0);}")

        self.SlowMinusButton = Qt.QPushButton(self)
        self.SlowMinusButton.setText("< -")
        self.SlowMinusButton.setMinimumWidth(35)
        # self.SlowMinusButton.setFixedHeight(20)
        self.SlowMinusButton.setStyleSheet("QPushButton {font:12pt; font-weight: bold; \
                                                         background-color:rgb(220,0,0);}")

        # self.StopButton = Qt.QPushButton(self)
        # self.StopButton.setText("STOP")
        # self.StopButton.setMinimumWidth(35)
        # # self.SlowPlusButton.setFixedHeight(20)
        # self.StopButton.setStyleSheet("QPushButton {font:12pt; background-color:rgb(220,0,0);}")

        self.SlowPlusButton = Qt.QPushButton(self)
        self.SlowPlusButton.setText("+ >")
        self.SlowPlusButton.setMinimumWidth(35)
        # self.SlowPlusButton.setFixedHeight(20)
        self.SlowPlusButton.setStyleSheet("QPushButton {font:12pt; font-weight: bold; \
                                                         background-color:rgb(220,0,0);}")

        self.FastPlusButton = Qt.QPushButton(self)
        self.FastPlusButton.setText("+ >>")
        self.FastPlusButton.setMinimumWidth(35)
        # self.FastPlusButton.setFixedHeight(20)
        self.FastPlusButton.setStyleSheet("QPushButton {font:12pt; font-weight: bold; \
                                                         background-color:rgb(220,0,0);}")

        hbox1 = Qt.QHBoxLayout()
        hbox1.addWidget(self.FastMinusButton)
        hbox1.addWidget(self.SlowMinusButton)
        # hbox1.addWidget(self.StopButton)
        hbox1.addWidget(self.SlowPlusButton)
        hbox1.addWidget(self.FastPlusButton)
        hbox1.setSpacing(1)
        self.setLayout(hbox1)

    def connect_signals(self):
        self.FastMinusButton.pressed.connect(self._button_pressed_event)
        self.SlowMinusButton.pressed.connect(self._button_pressed_event)
        # self.StopButton.pressed.connect(self._button_release_event)
        self.SlowPlusButton.pressed.connect(self._button_pressed_event)
        self.FastPlusButton.pressed.connect(self._button_pressed_event)

        self.FastMinusButton.released.connect(self._button_release_event)
        self.SlowMinusButton.released.connect(self._button_release_event)
        self.SlowPlusButton.released.connect(self._button_release_event)
        self.FastPlusButton.released.connect(self._button_release_event)

    def _button_pressed_event(self):
        sender = self.sender()
        if "<<" in sender.text() or ">>" in sender.text():
            self.speed = "fast"
        elif "<" in sender.text() or ">" in sender.text():
            self.speed = "slow"

        if "+" in sender.text():
            self.direction = "in"
        elif "-" in sender.text():
            self.direction = "out"

        msg={
            "type":"autostar",
            "cmd":"focus",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "speed": self.speed,
                "direction": self.direction,
            }
        }

        self.focusSignal.emit(msg)

    def _button_release_event(self):
        msg={
            "type":"autostar",
            "cmd":"focus_stop",
            'src': 'GUI_Thread',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        self.focusSignal.emit(msg)
