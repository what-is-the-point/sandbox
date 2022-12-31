#!/usr/bin/env python3
#

#import numpy
#import time

# First Qt and 2nd Qt are different.  You'll get errors if they're both not available,
# hence the import-as to avoid name collisions
import numpy as np
from PyQt5 import Qt
from PyQt5.QtCore import Qt as Qtc
from PyQt5.QtCore import pyqtSignal, QPoint, pyqtProperty, QRect
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PyQt5.QtGui import QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon, QColor, QBrush

from gui.lcd_feedback_frame import *

class ElevationDialFrame(QGroupBox):
    def __init__(self, lbl, cfg):
        QFrame.__init__(self)
        self.setMinimumSize(100, 100)
        self.lbl = lbl
        self.setTitle(self.lbl)
        self.setContentsMargins(1,4,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.cfg = cfg
        self.angle_min  = self.cfg['min']
        self.angle_max  = self.cfg['max']
        self.cur_angle = 0.0
        self.com_angle = 20.0
        self.tar_angle = 40.0
        self.initUI()

    def initUI(self):
        self.ElevationDial = ElevationDial(self.lbl, self.cfg)
        self.cur_lcd = LCD(self,255,0,0)
        self.com_lcd = LCD(self,0,100,255)
        self.tar_lcd = LCD(self,0,255,50)
        lcd_hbox = Qt.QHBoxLayout()
        lcd_hbox.addWidget(self.cur_lcd)
        lcd_hbox.addWidget(self.com_lcd)
        lcd_hbox.addWidget(self.tar_lcd)
        grid = Qt.QGridLayout()
        grid.setSpacing(0)
        grid.addWidget(self.ElevationDial,0,0,1,1)
        grid.addLayout(lcd_hbox,1,0,1,1)
        self.setLayout(grid)
        self.show()

    def update_current_angle(self, cur_angle):
        if cur_angle != self.cur_angle:
            if   cur_angle < self.angle_min: self.cur_angle = self.angle_min  # Angle will already be negative
            elif cur_angle > self.angle_max: self.cur_angle = self.angle_max  # Angle will already be negative
            else: self.cur_angle = cur_angle
        self.ElevationDial.update_current_angle(self.cur_angle)
        self.cur_lcd.display(self.cur_angle)

    def update_command_angle(self, com_angle):
        if com_angle != self.com_angle:
            if   com_angle < self.angle_min: self.com_angle = self.angle_min  # Angle will already be negative
            elif com_angle > self.angle_max: self.com_angle = self.angle_max  # Angle will already be negative
            else: self.com_angle = com_angle
        self.ElevationDial.update_command_angle(self.com_angle)
        self.com_lcd.display(self.com_angle)

    def update_target_angle(self, tar_angle):
        if tar_angle != self.tar_angle:
            if   tar_angle < self.angle_min: self.tar_angle = self.angle_min  # Angle will already be negative
            elif tar_angle > self.angle_max: self.tar_angle = self.angle_max  # Angle will already be negative
            else: self.tar_angle = tar_angle
        self.ElevationDial.update_target_angle(self.tar_angle)
        self.tar_lcd.display(self.tar_angle)

class ElevationDial(QWidget):
    def __init__(self,lbl,cfg):
        QWidget.__init__(self, None)
        self.setMinimumSize(100, 100)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self._margins = 1
        self.lbl = lbl
        self.cfg = cfg

        # Set parameters
        self.with_rate  = self.cfg['rate_dial']
        self.rate_max   = self.cfg['rate_max']
        self.rate_min   = self.cfg['rate_min']
        self.angle_min  = self.cfg['min']
        self.angle_max  = self.cfg['max']
        self.rateType   = 'colorbar' #might make this a bar indicator later

        self.cur_angle  = 0.0
        self.com_angle  = 20.0
        self.tar_angle  = 40.0

        self.backgroundColor = QColor(0,0,0)
        self.scaleColor      = QColor(255,255,255)
        self.dialColor       = QColor(100,100,100)
        self.curNeedleColor  = QColor(255,0,0)
        self.comNeedleColor  = QColor(0,100,255)
        # self.tarNeedleColor  = QColor(255,0,255)
        self.tarNeedleColor  = QColor(0,255,50)

        self.startAngle = 0.0
        self.endAngle = 90
        self.degScaler = 16.0 # The span angle must be specified in 1/16 of a degree units
        self.scale = 1.4
        self.h_offset = 5
        self.darken()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.drawMarkings(painter)
        self.drawNeedle(painter, which='current')
        self.drawNeedle(painter, which='command')
        # self.drawNeedle(painter, which='target')
        self.drawTargetTick(painter)
        self.drawCentralDial(painter)
        painter.end()

    def drawMarkings(self, painter):
        painter.save()
        painter.translate(self.width()/1.2, self.height()/1.15-self.h_offset)
        painter.scale(self.scale, self.scale)

        #define text and setup font info
        font = QFont(self.font())
        pixelSize = 6
        font.setPixelSize(pixelSize)
        metrics = QFontMetricsF(font)
        painter.setFont(font)

        painter.rotate(-95)
        tickInterval = 5
        arcRad = int(min(self.width()/2, self.height()/2))
        i = -5
        longTick = 12
        shortTick= 6
        while i <= self.endAngle+5:
            if (i < 0) or (i>self.endAngle):
                font.setPixelSize(7)
                painter.setPen(QPen(QColor(255,0,0)))
            else:
                font.setPixelSize(10)
                painter.setPen(QPen(QColor(self.scaleColor),1.25))
            metrics = QFontMetricsF(font)
            painter.setFont(font)

            if (i == -5) or (i==95):
                painter.drawLine(0, -(arcRad - shortTick), 0, -arcRad)
            if i == 0 or i==90:
                painter.drawLine(0, -longTick, 0, -arcRad)
                painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -arcRad-10, "{:d}".format(i))
            elif i % 15 == 0:
                painter.drawLine(0, -(arcRad - longTick), 0, -arcRad)
                painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -arcRad-10, "{:d}".format(i))
            else:
                painter.drawLine(0, -(arcRad - shortTick), 0, -arcRad)
            painter.rotate(tickInterval)
            i += tickInterval



        painter.restore()

    def drawCentralDial(self,painter):
        painter.save()
        painter.translate(self.width()/1.2, self.height()/1.15-self.h_offset)
        painter.scale(self.scale, self.scale)

        #draw inner circle
        brush = self.palette().brush(QPalette.Highlight)
        brush.setColor(self.dialColor)
        painter.setBrush(brush)
        #painter.setPen(QPen(self.scaleColor, 1/2))
        painter.setPen(QPen(Qtc.NoPen))
        painter.setRenderHint(QPainter.Antialiasing)
        fixed_radius = 6
        center = QPoint(0, 0)
        painter.drawEllipse(center, fixed_radius,fixed_radius)
        painter.restore()

    def drawNeedle(self, painter, which="current"):
        painter.save()
        painter.translate(self.width()/1.2, self.height()/1.15-self.h_offset)
        painter.scale(self.scale, self.scale)
        painter.setPen(QPen(Qtc.NoPen))

        # Rotate surface for painting
        painter.rotate(-90)
        if which == 'current':
            intAngle = int(round(self.cur_angle))
            needleTipColor = QColor(self.curNeedleColor)
        if which == 'command':
            intAngle = int(round(self.com_angle))
            needleTipColor = QColor(self.comNeedleColor)
        if which == 'target':
            intAngle = int(round(self.tar_angle))
            needleTipColor = QColor(self.tarNeedleColor)
        painter.rotate(intAngle)

        # Set up the brush
        needleTipBrush = self.palette().brush(QPalette.Highlight)
        # needleTipColor = QColor(self.curNeedleColor)
        needleTipBrush.setColor(needleTipColor)
        painter.setBrush(needleTipBrush)
        # draw the needle
        needle_length = int(min(self.width()/2,self.height()/2))
        if which == 'current':
            painter.drawPolygon(QPolygon([QPoint(0,-needle_length),QPoint(4,-2),QPoint(-4,-2)]))
        if which == 'command':
            painter.drawPolygon(QPolygon([QPoint(0,-needle_length),QPoint(2,-2),QPoint(-2,-2)]))
        if which == 'target':
            painter.drawPolygon(QPolygon([QPoint(0,-needle_length),QPoint(2,-2),QPoint(-2,-2)]))
        painter.restore()

    def drawTargetLine(self,painter):
        painter.save()
        # Set up painter
        painter.translate(self.width()/1.2, self.height()/1.15-self.h_offset)
        painter.scale(self.scale, self.scale)
        #painter.setPen(QPen(Qtc.NoPen))

        font = QFont(self.font())
        font.setPixelSize(6)
        metrics = QFontMetricsF(font)
        painter.setFont(font)
        painter.setPen(QPen(self.tarNeedleColor))

        # Rotate surface for painting
        painter.rotate(-90)
        intAngle = int(round(self.tar_angle))
        painter.rotate(intAngle)

        arcRad = int(min(self.width()/2, self.height()/2))
        painter.drawLine(0, -(arcRad - 10), 0, -(arcRad+4))
        painter.restore()

    def drawTargetTick(self,painter):
        painter.save()
        painter.translate(self.width()/1.2, self.height()/1.15-self.h_offset)
        painter.scale(self.scale, self.scale)
        painter.setPen(QPen(Qtc.NoPen))
        painter.rotate(-90)
        intAngle = int(round(self.tar_angle))
        painter.rotate(intAngle)
        needleTipBrush = self.palette().brush(QPalette.Highlight)
        needleTipColor = QColor(self.tarNeedleColor)
        needleTipBrush.setColor(needleTipColor)
        painter.setBrush(needleTipBrush)
        arcRad = int(min(self.width()/2,self.height()/2))
        tickWidth = 3
        tickHeight = 8
        painter.drawPolygon(QPolygon([QPoint(0,-arcRad+8),
                                      QPoint(tickWidth,-arcRad-tickHeight),
                                      QPoint(-tickWidth,-arcRad-tickHeight)]))


        painter.restore()


    def _map(self, val, src_min, src_max, dst_min, dst_max):
        """
        Scale the given value from the scale of src to the scale of dst.
        """
        return ((val - src_min) / (src_max-src_min)) * (dst_max-dst_min) + dst_min

    def cur_angle(self):
        return self.cur_angle

    def tar_angle(self):
        return self.tar_angle

    def rate(self):
        return self.rate

    def update_current_angle(self, cur_angle):
        self.cur_angle = cur_angle
        #self.currentAngleChanged.emit(cur_angle)
        self.update()

    # cur_angle = pyqtProperty(float, cur_angle, update_current_angle)
    def update_command_angle(self, com_angle):
        self.com_angle = com_angle
        #self.targetAngleChanged.emit(tar_angle)
        self.update()

    def update_target_angle(self, tar_angle):
        self.tar_angle = tar_angle
        #self.targetAngleChanged.emit(tar_angle)
        self.update()

    #tar_angle = pyqtProperty(float, tar_angle, update_target_angle)

    def update_rate(self, rate):
        self.rate = rate
        alpha = self._map(abs(self.rate),0, self.rate_max, 50,200)
        self.rateNeedleColor = QColor(255,0,255,alpha)
        #self.rateChanged.emit(rate)
        self.update()

    #rate = pyqtProperty(float, rate, update_rate)

    def darken(self):
        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Background,QColor(0,0,0))
        palette.setColor(Qt.QPalette.WindowText,QColor(0,0,0))
        palette.setColor(Qt.QPalette.Text,self.dialColor)
        self.setPalette(palette)
