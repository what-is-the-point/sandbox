#!/usr/bin/env python
#version 2.1

from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5 import Qt


class LCD(Qt.QLCDNumber):
    def __init__(self, parent=None, r=0,g=0,b=0):
        super(LCD, self).__init__(parent)
        self.setSegmentStyle(Qt.QLCDNumber.Flat)
        #self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.setDecMode()
        self.setNumDigits(6)

        palette = Qt.QPalette(self.palette())
        palette.setColor(palette.Background,QtCore.Qt.transparent)
        palette.setColor(palette.Foreground,Qt.QColor(r,g,b))
        self.setPalette(palette)
        self.setFixedHeight(30)
        self.display(000.00)

class lcd_feedback_frame(Qt.QFrame):
    def __init__(self, parent=None):
        super(lcd_feedback_frame, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        #self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.initWidgets()

    def initWidgets(self):
        self.cur_lcd = LCD(self,255,0,0)
        self.com_lcd = LCD(self,0,100,255)
        self.tar_lcd = LCD(self,0,255,50)

        lcd_hbox = Qt.QHBoxLayout()
        lcd_hbox.addWidget(self.cur_lcd)
        lcd_hbox.addWidget(self.com_lcd)
        lcd_hbox.addWidget(self.tar_lcd)
        self.setLayout(lcd_hbox)

    def set_current(self,val):
        self.cur_lcd.display(val)

    def set_rate(self,val):
        self.com_lcd.display(val)

    def set_target(self,val):
        self.tar_lcd.display(val)
