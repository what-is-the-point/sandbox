#!/usr/bin/env python
#version 2.1

from PyQt5 import Qt
from PyQt5 import QtCore
from functools import partial
import math

class slew_frame(Qt.QFrame):
    def __init__(self, parent=None):
        super(slew_frame, self).__init__()
        self.parent = parent
        self.az_speed = 9
        self.el_speed = 9
        self.initUI()

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        self.setMinimumSize(200, 200)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.initWidgets()
        self.connect_signals()

    def initWidgets(self):
        pixmap = Qt.QPixmap("./icons/arrow.png")
        base = pixmap.transformed(Qt.QTransform().rotate(-90))

        arrow_u = Qt.QIcon(base)
        arrow_r  = Qt.QIcon(base.transformed(Qt.QTransform().rotate(90)))
        arrow_l  = Qt.QIcon(base.transformed(Qt.QTransform().rotate(270)))
        arrow_d  = Qt.QIcon(base.transformed(Qt.QTransform().rotate(180)))

        arrow_ur = base.transformed(Qt.QTransform().rotate(45))
        x = (arrow_ur.width() - base.width()) / 2
        y = (arrow_ur.height() - base.height()) / 2
        arrow_ur = Qt.QIcon(arrow_ur.copy(x,y,base.width(), base.height()))

        arrow_dr = Qt.QIcon(base.transformed(Qt.QTransform().rotate(135)).copy(x,y,base.width(), base.height()))
        arrow_dl = Qt.QIcon(base.transformed(Qt.QTransform().rotate(225)).copy(x,y,base.width(), base.height()))
        arrow_ul = Qt.QIcon(base.transformed(Qt.QTransform().rotate(315)).copy(x,y,base.width(), base.height()))

        btn_size = 20

        frame_lbl = Qt.QLabel("Slew Controls:")
        frame_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        frame_lbl.setStyleSheet("QLabel {font:12pt; font-weight:bold; text-decoration: underline; color:rgb(255,0,0);}")
        frame_lbl.setFixedWidth(200)
        frame_lbl.setFixedHeight(20)

        #Top Row of buttons
        self.ulButton = Qt.QPushButton(self)
        self.ulButton.setIcon(arrow_ul)
        self.ulButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.ulButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        self.uButton = Qt.QPushButton(self)
        self.uButton.setIcon(arrow_u)
        self.uButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.uButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        self.urButton = Qt.QPushButton(self)
        self.urButton.setIcon(arrow_ur)
        self.urButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.urButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        top_hbox = Qt.QHBoxLayout()
        top_hbox.addWidget(self.ulButton)
        top_hbox.addWidget(self.uButton)
        top_hbox.addWidget(self.urButton)

        #Middle Row of buttons
        self.lButton = Qt.QPushButton(self)
        self.lButton.setIcon(arrow_l)
        self.lButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.lButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        self.stopButton = Qt.QPushButton(self)
        pixmap = Qt.QPixmap("./icons/stop.png")
        self.stopButton.setIcon(Qt.QIcon(pixmap))
        self.stopButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.stopButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        self.rButton = Qt.QPushButton(self)
        self.rButton.setIcon(arrow_r)
        self.rButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.rButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        middle_hbox = Qt.QHBoxLayout()
        middle_hbox.addWidget(self.lButton)
        middle_hbox.addWidget(self.stopButton)
        middle_hbox.addWidget(self.rButton)

        #Bottom Row of Buttons
        self.dlButton = Qt.QPushButton(self)
        self.dlButton.setIcon(arrow_dl)
        self.dlButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.dlButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        self.dButton = Qt.QPushButton(self)
        self.dButton.setIcon(arrow_d)
        self.dButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.dButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        self.drButton = Qt.QPushButton(self)
        self.drButton.setIcon(arrow_dr)
        self.drButton.setIconSize(Qt.QSize(btn_size,btn_size))
        #self.drButton.setStyleSheet("QPushButton { background-color:rgb(200,0,0); }")
        bottom_hbox = Qt.QHBoxLayout()
        bottom_hbox.addWidget(self.dlButton)
        bottom_hbox.addWidget(self.dButton)
        bottom_hbox.addWidget(self.drButton)

        #Controls for Azimuth Motor Speed
        lbl = Qt.QLabel("Azimuth Speed:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        #lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(100)
        self.slewAzSpeedSlider = Qt.QSlider(QtCore.Qt.Horizontal)
        self.slewAzSpeedSlider.setMaximum(9)
        self.slewAzSpeedSlider.setMinimum(1)
        self.slewAzSpeedSlider.setValue(9)
        #self.slewAzSpeedSlider.setStyleSheet("QSlider {background-color:rgb(0,0,0); color:rgb(200,0,0)}")
        self.slewAzLabel = Qt.QLabel("{:d}".format(self.az_speed))
        self.slewAzLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        #self.slewAzLabel.setStyleSheet("QLabel {color:rgb(255,0,0);}")
        az_hbox = Qt.QHBoxLayout()
        az_hbox.addWidget(lbl)
        az_hbox.addWidget(self.slewAzSpeedSlider)
        az_hbox.addWidget(self.slewAzLabel)

        #Controls for Elevation Motor Speed
        lbl = Qt.QLabel("Elevation Speed:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        #lbl.setStyleSheet("QLabel { font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(100)
        self.slewElSpeedSlider = Qt.QSlider(QtCore.Qt.Horizontal)
        self.slewElSpeedSlider.setMaximum(9)
        self.slewElSpeedSlider.setMinimum(1)
        self.slewElSpeedSlider.setValue(9)
        #self.slewElSpeedSlider.setStyleSheet("QSlider {background-color:rgb(0,0,0); color:rgb(200,0,0)}")
        self.slewElLabel = Qt.QLabel("{:d}".format(self.el_speed))
        self.slewElLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        #self.slewElLabel.setStyleSheet("QLabel {color:rgb(255,0,0);}")
        el_hbox = Qt.QHBoxLayout()
        el_hbox.addWidget(lbl)
        el_hbox.addWidget(self.slewElSpeedSlider)
        el_hbox.addWidget(self.slewElLabel)

        self.lock_cb = Qt.QCheckBox('Synchronize Speeds', self)
        self.lock_cb.setStyleSheet("QCheckBox { font:10pt; background-color:rgb(0,0,0); color:rgb(255,0,0); }")
        self.lock_cb.setChecked(True)

        vbox = Qt.QVBoxLayout()
        vbox.addWidget(frame_lbl)
        vbox.addLayout(top_hbox)
        vbox.addLayout(middle_hbox)
        vbox.addLayout(bottom_hbox)
        vbox.addLayout(az_hbox)
        vbox.addLayout(el_hbox)
        vbox.addWidget(self.lock_cb)
        vbox.addStretch(1)
        self.setLayout(vbox)

    def connect_signals(self):
        self.slewAzSpeedSlider.valueChanged.connect(self.set_az_speed)
        self.slewElSpeedSlider.valueChanged.connect(self.set_el_speed)
        self.lock_cb.stateChanged.connect(self.lock_cb_handler)

        self.ulButton.pressed.connect(lambda: self.parent.slew_up_left(self.az_speed, self.el_speed))
        self.ulButton.released.connect(self.parent.slew_stop)

        self.uButton.pressed.connect(lambda: self.parent.slew_up(self.el_speed))
        self.uButton.released.connect(self.parent.slew_stop)

        self.urButton.pressed.connect(lambda: self.parent.slew_up_right(self.az_speed, self.el_speed))
        self.urButton.released.connect(self.parent.slew_stop)

        self.lButton.pressed.connect(lambda: self.parent.slew_left(self.az_speed))
        self.lButton.released.connect(self.parent.slew_stop)

        self.stopButton.pressed.connect(self.parent.slew_stop)

        self.rButton.pressed.connect(lambda: self.parent.slew_right(self.az_speed))
        self.rButton.released.connect(self.parent.slew_stop)

        self.dlButton.pressed.connect(lambda: self.parent.slew_down_left(self.az_speed, self.el_speed))
        self.dlButton.released.connect(self.parent.slew_stop)

        self.dButton.pressed.connect(lambda: self.parent.slew_down(self.el_speed))
        self.dButton.released.connect(self.parent.slew_stop)

        self.drButton.pressed.connect(lambda: self.parent.slew_down_right(self.az_speed, self.el_speed))
        self.drButton.released.connect(self.parent.slew_stop)


    def lock_cb_handler(self, state):
        if (state == QtCore.Qt.Checked):
            self.el_speed = self.az_speed
            self.slewElSpeedSlider.setValue(self.el_speed)

    def set_az_speed(self, val):
        self.az_speed = val
        print("Set Az Slew Speed: {:d}".format(self.az_speed))
        self.slewAzLabel.setText("{:d}".format(self.az_speed))

        if (self.lock_cb.checkState() == Qt.Qt.Checked):
            self.el_speed = val
            self.slewElSpeedSlider.setValue(val)

    def set_el_speed(self, val):
        self.el_speed = val
        print("Set El Slew Speed: {:d}".format(self.el_speed))
        self.slewElLabel.setText("{:d}".format(self.el_speed))

        if (self.lock_cb.checkState() == Qt.Qt.Checked):
            self.az_speed = val
            self.slewAzSpeedSlider.setValue(val)

    def get_slew_speed(self):
        return self.az_speed, self.el_speed
