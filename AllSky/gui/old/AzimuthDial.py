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
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon, QColor, QBrush

class AzimuthDialFrame(QFrame):
    def __init__(self, lbl, cfg):
        QFrame.__init__(self)
        self.setMinimumSize(100, 100)
        self.lbl = lbl
        self.cfg = cfg
        self.with_rate  = self.cfg['rate_dial']
        self.rate_max   = self.cfg['rate_max']
        self.rate_min   = self.cfg['rate_min']
        self.angle_min  = self.cfg['min']
        self.angle_max  = self.cfg['max']
        self.cur_angle = 0.0
        self.tar_angle = 0.0
        self.rate      = 0.0
        self.initUI()

    def initUI(self):
        self.AzimuthDial = AzimuthDial(self.lbl, self.cfg)
        grid = Qt.QGridLayout()
        grid.setSpacing(0)
        grid.addWidget(self.AzimuthDial,0,0,1,1)
        self.setLayout(grid)
        self.show()

    def update_current_angle(self, cur_angle):
        if cur_angle != self.cur_angle:
            if   cur_angle < self.angle_min: self.cur_angle = self.angle_min  # Angle will already be negative
            elif cur_angle > self.angle_max: self.cur_angle = self.angle_max  # Angle will already be negative
            else: self.cur_angle = cur_angle
        self.AzimuthDial.update_current_angle(self.cur_angle)
        # self.cur_lbl.setText("{:03.2f}".format(cur_angle))

    def update_target_angle(self, tar_angle):
        if tar_angle != self.tar_angle:
            if   tar_angle < self.angle_min: self.tar_angle = self.angle_min  # Angle will already be negative
            elif tar_angle > self.angle_max: self.tar_angle = self.angle_max  # Angle will already be negative
            else: self.tar_angle = tar_angle
        self.AzimuthDial.update_target_angle(self.tar_angle)
        # self.tar_lbl.setText("{:03.2f}".format(tar_angle))

    def update_rate(self, rate):
        if rate != self.rate:
            if   rate < self.rate_min: self.rate = self.rate_min  # Angle will already be negative
            elif rate > self.rate_max: self.rate = self.rate_max  # Angle will already be negative
            else: self.rate = rate
        self.AzimuthDial.update_rate(self.rate)

class AzimuthDial(QWidget):
    currentAngleChanged = pyqtSignal(float)
    targetAngleChanged = pyqtSignal(float)
    rateChanged = pyqtSignal(float)

    def __init__(self,lbl,cfg):
        QWidget.__init__(self, None)
        self.setMinimumSize(200, 200)
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
        self.rateType   = 'needle' #might make this a bar indicator later

        self.cur_angle  = 0.0
        self.tar_angle  = 0.0
        self.rate       = 0.0

        self.backgroundColor = QColor(0,0,0)
        self.scaleColor      = QColor(255,255,255)
        self.dialColor       = QColor(100,100,100)
        self.curNeedleColor  = QColor(255,0,0)
        self.tarNeedleColor  = QColor(0,0,255)
        self.rateNeedleColor = QColor(255,0,255)

        self.startAngle = 0.0
        self.endAngle = 180.0
        self.degScaler = 16.0 # The span angle must be specified in 1/16 of a degree units

        self.darken()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.drawMarkings(painter)
        self.drawCurrentNeedle(painter)
        self.drawTargetNeedle(painter)
        if self.with_rate:
            self.drawRateMarkings(painter)
            if   self.rateType == 'needle'  : self.drawRateNeedle(painter)
            elif self.rateType == 'colorbar': self.drawRateColorBar(painter)
        self.drawCentralDial(painter)
        self.updateText(painter)
        painter.end()

    def drawMarkings(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(6)
        metrics = QFontMetricsF(font)
        painter.setFont(font)
        painter.setPen(QPen(QColor(self.scaleColor)))

        # Draw Tick Mark
        tickInterval = 5
        i = 0
        while i < 360:
            if i % 30 == 0:
                painter.drawLine(0, -45, 0, -50)
            else:
                painter.drawLine(0, -48, 0, -50)
            painter.rotate(tickInterval)
            i += tickInterval


        mark_min = 0
        painter.rotate(mark_min)
        mark_max = 330
        i = mark_min
        while i <= mark_max:
            font = QFont(self.font())
            if i % 30 == 0:
                if (i<0) or (i>=360):
                    font.setPixelSize(5)
                    metrics = QFontMetricsF(font)
                    painter.setFont(font)
                    painter.setPen(QPen(QColor(255,0,0)))
                    if i==mark_min:
                        # painter.drawText(-metrics.width("{:d} ".format(int(i/2.0)), -40, "{:d}".format(int(i))))
                        painter.drawText(int(i/2.0), -40, int(i))
                        painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -40, " {:d}".format(i))
                    elif i==mark_max:
                        painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -36, "{:d}".format(i))
                    else:
                        painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -40, "{:d}".format(i))
                else:
                    font.setPixelSize(6)
                    metrics = QFontMetricsF(font)
                    painter.setFont(font)
                    painter.setPen(QPen(QColor(self.scaleColor)))
                    # painter.drawText(-metrics.width("{:d}".format(int(i/2.0)), -52, "{:d}".format(int(i))))
                    painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -52, "{:d}".format(i))

            painter.rotate(tickInterval)
            i += tickInterval

        painter.restore()

    def drawCentralDial(self,painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        #draw inner circle
        brush = self.palette().brush(QPalette.Highlight)
        brush.setColor(self.dialColor)
        painter.setBrush(brush)
        #painter.setPen(QPen(self.scaleColor, 1/2))
        painter.setPen(QPen(Qtc.NoPen))
        painter.setRenderHint(QPainter.Antialiasing)
        fixed_radius = 5
        center = QPoint(0, 0)
        painter.drawEllipse(center, fixed_radius,fixed_radius)
        painter.restore()

    def updateText(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        #define text and setup font info
        font = QFont(self.font())
        pixelSize = 6
        font.setPixelSize(pixelSize)
        metrics = QFontMetricsF(font)
        painter.setFont(font)

        curAngleStr = "{:03.2f}".format(self.cur_angle)
        tarAngleStr = "{:03.2f}".format(self.tar_angle)
        rateStr     = "{:03.2f}".format(self.rate)

        font.setUnderline(True)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(self.scaleColor)))
        painter.drawText(-60, -56, self.lbl)
        font.setUnderline(False)
        #font.setBold(False)
        painter.setFont(font)
        painter.setPen(QPen(QColor(self.curNeedleColor)))
        painter.drawText(-60, int(-46+(-pixelSize/2)), curAngleStr)
        painter.setPen(QPen(QColor(self.tarNeedleColor)))
        painter.drawText(-60, int(-46+pixelSize/2-1), tarAngleStr)
        if self.with_rate:
            painter.setPen(QPen(QColor(self.rateNeedleColor)))
            painter.drawText(-60, int(-46+pixelSize+pixelSize/2-2), rateStr)
        painter.restore()

    def drawRateMarkings(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(6)
        metrics = QFontMetricsF(font)
        painter.setFont(font)

        startAngle = int(round(self.startAngle * self.degScaler, 0))
        endAngle   = int(round(self.endAngle   * self.degScaler, 0))

        painter.setPen(QPen(QColor(self.scaleColor), 0.5))
        needleTipBrush = self.palette().brush(QPalette.Highlight)
        needleTipBrush.setColor(self.backgroundColor)
        painter.setBrush(needleTipBrush)

        arcRad = 20
        painter.drawArc(-arcRad,-arcRad,arcRad*2,arcRad*2, startAngle, endAngle)
        painter.rotate(-90)
        step_deg = 9 #-10 to 10 increment marks
        ticks = 21
        deg_p_tick = int((self.rate_max - self.rate_min)/(ticks-1))
        minor_tick = -(arcRad-2)
        major_tick = -(arcRad-4)
        i=int(self.rate_min)
        step=0
        while step <= 180:
            if (step-90) % 45 == 0:
                if (step==0) or (step==180):
                    painter.drawLine(0, -(arcRad), 0, arcRad)
                else:
                    painter.drawLine(0, -(arcRad), 0, major_tick)
                painter.drawText(int(-metrics.width("{:d}".format(i))/2.0), -(arcRad+1), "{:d}".format(i))
            else:
                painter.drawLine(0, -(arcRad), 0, minor_tick)
            painter.rotate(step_deg)
            step+=step_deg
            i += deg_p_tick

        painter.restore()

    def drawCurrentNeedle(self, painter):
        painter.save()
        # Set up painter
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        painter.setPen(QPen(Qtc.NoPen))

        # Rotate surface for painting
        intAngle = int(round(self.cur_angle))
        painter.rotate(intAngle)

        # Set up the brush
        needleTipBrush = self.palette().brush(QPalette.Highlight)
        needleTipColor = QColor(self.curNeedleColor)
        needleTipBrush.setColor(needleTipColor)
        painter.setBrush(needleTipBrush)
        # draw the needle
        painter.drawPolygon(QPolygon([QPoint(0,-50),QPoint(3,-2),QPoint(-3,-2)]))
        painter.restore()

    def drawTargetNeedle(self, painter):
        painter.save()
        # Set up painter
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        painter.setPen(QPen(Qtc.NoPen))

        # Rotate surface for painting
        intAngle = int(round(self.tar_angle))
        painter.rotate(intAngle)

        needleTipBrush = self.palette().brush(QPalette.Highlight)
        needleTipColor = QColor(self.tarNeedleColor)
        needleTipBrush.setColor(needleTipColor)
        painter.setBrush(needleTipBrush)
        painter.drawPolygon(QPolygon([QPoint(0,-50),QPoint(1,-2),QPoint(-1,-2)]))
        painter.restore()

    def drawRateNeedle(self, painter):
        painter.save()
        # Set up painter
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        painter.setPen(QPen(Qtc.NoPen))

        needleTipBrush = self.palette().brush(QPalette.Highlight)
        needleTipBrush.setColor(self.rateNeedleColor)
        painter.setBrush(needleTipBrush)

        # Rotate surface for painting
        painter.rotate(self._map(self.rate,self.rate_min, self.rate_max, -90,90))
        needleLength = 20
        painter.drawPolygon(QPolygon([QPoint(-1,-5), QPoint(1,-5), QPoint(0,-needleLength)]))
        painter.restore()

    def drawRateColorBar(self, painter):
        painter.save()
        # Set up painter
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        spanAngle = 90 - self._map(self.rate, self.rate_min, self.rate_max, 0, 180)
        if self.rate < 0:
            print("ping")
            spanAngle = spanAngle
            startAngle = 90
        else:
            print("pong")
            spanAngle = spanAngle
            startAngle = 90
        print(self.rate,startAngle, spanAngle )

        #startAngle = int(round(self.startAngle * self.degScaler, 1))
        #spanAngle  = int(round(spanAngle * self.degScaler, 1))
        startAngle = startAngle * self.degScaler
        spanAngle  = spanAngle * self.degScaler

        self.penWidth = 2
        self.halfPenWidth = int(self.penWidth / 2)

        alpha = self._map(abs(self.rate),0, self.rate_max, 0,255)
        painter.setPen(QPen(QColor(255,0,255,alpha), self.penWidth))

        dia = 20 - self.halfPenWidth
        painter.rotate(0)
        painter.drawArc(-dia,-dia,dia*2,dia*2, startAngle, spanAngle)


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

    #cur_angle = pyqtProperty(float, cur_angle, update_current_angle)

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
        palette.setColor(Qt.QPalette.Text,QColor(0,255,0))
        self.setPalette(palette)
