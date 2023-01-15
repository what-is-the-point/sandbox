#!/usr/bin/env python3
#-- coding: utf-8 --

from PyQt5 import QtCore
from PyQt5 import Qt


class sync_frame(Qt.QFrame):
    def __init__(self, parent=None):
        super(sync_frame, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        lbl_width = 50
        val_width = 125
        lbl_height = 12
        btn_height = 20

        frame_lbl = Qt.QLabel("Sync Controls:")
        frame_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        frame_lbl.setStyleSheet("QLabel {font:12pt; font-weight:bold; text-decoration: underline; color:rgb(255,0,0);}")
        frame_lbl.setFixedWidth(200)
        frame_lbl.setFixedHeight(20)

        self.azLabel = Qt.QLabel("Sync Azimuth:")
        self.azLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.azLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.azTextBox = Qt.QLineEdit()
        self.azTextBox.setText("000.000")
        self.azTextBox.setInputMask("#00.000;")
        self.azTextBox.setEchoMode(Qt.QLineEdit.Normal)
        self.azTextBox.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.azTextBox.setMaxLength(3)
        self.azTextBox.setFixedWidth(80)
        self.azTextBox.setFixedHeight(20)
        az_hbox = Qt.QHBoxLayout()
        az_hbox.addWidget(self.azLabel)
        az_hbox.addWidget(self.azTextBox)

        self.elLabel = Qt.QLabel("Sync Elevation:")
        self.elLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.elLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.elTextBox = Qt.QLineEdit()
        self.elTextBox.setText("00.000")
        self.elTextBox.setInputMask("#00.000;")
        self.elTextBox.setEchoMode(Qt.QLineEdit.Normal)
        self.elTextBox.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.elTextBox.setMaxLength(3)
        self.elTextBox.setFixedWidth(80)
        self.elTextBox.setFixedHeight(20)
        el_hbox = Qt.QHBoxLayout()
        el_hbox.addWidget(self.elLabel)
        el_hbox.addWidget(self.elTextBox)

        self.syncButton = Qt.QPushButton("Sync")
        self.syncButton.setFixedHeight(btn_height)
        self.syncButton.setStyleSheet("QPushButton { font:10pt; background-color:rgb(200,0,0); }")

        vbox = Qt.QVBoxLayout()
        vbox.addWidget(frame_lbl)
        vbox.addLayout(az_hbox)
        vbox.addLayout(el_hbox)
        vbox.addWidget(self.syncButton)
        self.setLayout(vbox)


    def connect_signals(self):
        self.syncButton.clicked.connect(self.syncButton_event)
        pass


    def syncButton_event(self):
        self.tar_az = float(self.azTextBox.text())
        self.tar_el = float(self.elTextBox.text())
        self.parent.sync(self.tar_az, self.tar_el)
