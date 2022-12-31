#!/usr/bin/env python3
#version 2.1

from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtCore import pyqtSignal

class ControlButtonFrame(Qt.QFrame):
    decrementIncrementSignal = pyqtSignal(float)
    def __init__(self, parent=None, az_el = None):
        super(ControlButtonFrame, self).__init__()
        self.parent = parent
        self.az_el = az_el
        self.initUI()

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        self.MinusTenButton = Qt.QPushButton(self)
        self.MinusTenButton.setText("-10.0")
        self.MinusTenButton.setMinimumWidth(45)

        self.MinusOneButton = Qt.QPushButton(self)
        self.MinusOneButton.setText("-1.0")
        self.MinusOneButton.setMinimumWidth(45)

        self.MinusPtOneButton = Qt.QPushButton(self)
        self.MinusPtOneButton.setText("-0.1")
        self.MinusPtOneButton.setMinimumWidth(45)

        self.PlusPtOneButton = Qt.QPushButton(self)
        self.PlusPtOneButton.setText("+0.1")
        self.PlusPtOneButton.setMinimumWidth(45)

        self.PlusOneButton = Qt.QPushButton(self)
        self.PlusOneButton.setText("+1.0")
        self.PlusOneButton.setMinimumWidth(45)

        self.PlusTenButton = Qt.QPushButton(self)
        self.PlusTenButton.setText("+10.0")
        self.PlusTenButton.setMinimumWidth(45)

        hbox1 = Qt.QHBoxLayout()
        hbox1.addWidget(self.MinusTenButton)
        hbox1.addWidget(self.MinusOneButton)
        hbox1.addWidget(self.MinusPtOneButton)
        hbox1.addWidget(self.PlusPtOneButton)
        hbox1.addWidget(self.PlusOneButton)
        hbox1.addWidget(self.PlusTenButton)
        self.setLayout(hbox1)

    def connect_signals(self):
        self.PlusPtOneButton.clicked.connect(self.button_clicked)
        self.PlusOneButton.clicked.connect(self.button_clicked)
        self.PlusTenButton.clicked.connect(self.button_clicked)
        self.MinusPtOneButton.clicked.connect(self.button_clicked)
        self.MinusOneButton.clicked.connect(self.button_clicked)
        self.MinusTenButton.clicked.connect(self.button_clicked)

    def button_clicked(self):
        sender = self.sender()
        #print(float(sender.text()))
        self.decrementIncrementSignal.emit(float(sender.text()))
        #self.parent.increment_target_angle(self.az_el,float(sender.text()))
