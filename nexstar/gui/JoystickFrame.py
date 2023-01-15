#!/usr/bin/env python
#version 2.1

from PyQt5 import Qt
from PyQt5.QtCore import Qt as Qtc
from PyQt5.QtCore import pyqtSignal, QPoint, QPointF, pyqtProperty, QRect, QRectF, QLineF, QTimer
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PyQt5.QtGui import QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon, QColor, QBrush
from enum import Enum
import numpy as np
from queue import Queue
import datetime


DEG2RAD = np.pi / 180.0
RAD2DEG = 180.0 / np.pi

class Direction(Enum):
    Left = 0
    Right = 1
    Up = 2
    Down = 3

class JoystickFrame(QGroupBox):
    reportRates = pyqtSignal(dict)

    def __init__(self, cfg, parent=None):
        QGroupBox.__init__(self)
        #self.setMinimumSize(100, 100)
        #self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.setTitle(cfg['name'])
        self.setContentsMargins(1,4,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.az_rate_lim = cfg['az_rate_lim'] #fixed upper limit for az jog rate
        self.el_rate_lim = cfg['el_rate_lim'] #fixed upper limit for el jog rate
        self._az_rate_max = self.az_rate_lim #current az jog max rate
        self._el_rate_max = self.el_rate_lim #current el jog max rate

        self.az_rate = 0
        self.el_rate = 0
        self.q = Queue()
        self.initUI()
        self.connectSignals()

    def connectSignals(self):
        self.AzJogRateSlider.valueChanged.connect(self._set_az_rate_max)
        self.ElJogRateSlider.valueChanged.connect(self._set_el_rate_max)
        # self.reportRates.connect(self.updateRates)

        self.send_timer = QTimer(self)
        self.send_timer.setInterval(50)
        self.send_timer.timeout.connect(self.sendTimer_event)
        self.send_timer.start()
        pass

    def sendTimer_event(self):
        self.send_flag = True

    def updateRates(self, rates):
        if self.send_flag:
            self.reportRates.emit(rates)
            self.send_flag = False

    def _set_az_rate_max(self, val):
        self._az_rate_max = int(val)
        #print("Set Az Rate Max: {:d}".format(self._az_rate_max))
        self.joystick.set_az_rate_max(self._az_rate_max)
        self.AzJogRateLabel.setText("{:03d}".format(self._az_rate_max))

    def _set_el_rate_max(self, val):
        self._el_rate_max = int(val)
        #print("Set El Rate Max: {:d}".format(self._el_rate_max))
        self.joystick.set_el_rate_max(self._el_rate_max)
        self.ElJogRateLabel.setText("{:03d}".format(self._el_rate_max))

    def initUI(self):
        self.joystick = Joystick(self, az_rate_lim=self.az_rate_lim, el_rate_lim=self.el_rate_lim)
        self.AzJogRateSlider = Qt.QSlider(Qtc.Horizontal)
        self.AzJogRateSlider.setMaximum(self.az_rate_lim)
        self.AzJogRateSlider.setMinimum(0)
        self.AzJogRateSlider.setValue(self._az_rate_max)
        self.AzJogRateSlider.setTickInterval(1)
        self.AzJogRateSlider.setTickPosition(Qt.QSlider.TicksBothSides)
        self.AzJogRateSlider.setStyleSheet("QSlider {color:rgb(255,255,255);}")
        self.AzJogRateLabel = Qt.QLabel("{:03d}".format(self._az_rate_max))
        self.AzJogRateLabel.setAlignment(Qtc.AlignLeft|Qtc.AlignVCenter)
        self.AzJogRateLabel.setStyleSheet("QLabel {color:rgb(255,255,255);}")

        az_hbox = Qt.QHBoxLayout()
        az_hbox.addWidget(self.AzJogRateSlider)
        az_hbox.addWidget(self.AzJogRateLabel)

        self.ElJogRateSlider = Qt.QSlider(Qtc.Vertical)
        self.ElJogRateSlider.setMaximum(self.el_rate_lim)
        self.ElJogRateSlider.setMinimum(0)
        self.ElJogRateSlider.setValue(self._el_rate_max)
        self.ElJogRateSlider.setTickInterval(1)
        self.ElJogRateSlider.setTickPosition(Qt.QSlider.TicksBothSides)
        self.ElJogRateSlider.setStyleSheet("QSlider {color:rgb(255,255,255);}")
        self.ElJogRateLabel = Qt.QLabel("{:03d}".format(self._el_rate_max))
        self.ElJogRateLabel.setAlignment(Qtc.AlignLeft|Qtc.AlignVCenter)
        self.ElJogRateLabel.setStyleSheet("QLabel {color:rgb(255,255,255);}")

        el_vbox = Qt.QVBoxLayout()
        el_vbox.addWidget(self.ElJogRateLabel)
        el_vbox.addWidget(self.ElJogRateSlider)

        grid = Qt.QGridLayout()
        grid.setSpacing(0)
        grid.addLayout(el_vbox,0,0,1,1)
        grid.addWidget(self.joystick,0,1,1,1)
        grid.addLayout(az_hbox,1,1,1,1)
        self.setLayout(grid)
        self.show()

class Joystick(QWidget):
    reportRates = pyqtSignal(dict)

    def __init__(self, parent=None, az_rate_lim = 255, el_rate_lim=255):
        #super(Joystick, self).__init__(parent)

        QWidget.__init__(self, parent)
        self.setMinimumSize(140, 140)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.parent=parent

        self.az_rate_lim = az_rate_lim #fixed upper limit for az jog rate
        self._az_rate_max = self.az_rate_lim #current az jog max rate
        self.az_rate = 0
        self._az_dead_band = 1 #plus minus dead band for az joystick

        self.el_rate_lim = el_rate_lim #fixed upper limit for el jog rate
        self._el_rate_max = self.el_rate_lim #current el jog max rate
        self.el_rate = 0
        self._el_dead_band = 1 #plus minus dead band for az joystick

        self.joy_val = {
            "az_rate":0,
            "el_rate":0
        }

        self.reportRates.connect(self.parent.updateRates)

        self._margins = 1
        self.movingOffset = QPointF(0, 0)
        self.grabCenter = False
        self.__maxDistance = 50
        self.stickRad = 15
        self.scaleColor = QColor(255,0,0)
        self.knobColor  = QColor(200,75,75)

        self.darken()
        #self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.drawBounds(painter)
        self.drawKnob(painter)
        #self.updateText(painter)
        painter.end()

    def drawBounds(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        self.scale = min((self.width()  - self._margins)/120.0,
                         (self.height() - self._margins)/120.0)
        painter.scale(self.scale, self.scale)

        font = QFont(self.font())
        font.setPixelSize(1)
        metrics = QFontMetricsF(font)
        painter.setFont(font)
        painter.setPen(QPen(QColor(self.scaleColor), 0.75))

        painter.drawLine(0, 55,0,-55)
        painter.drawLine(55, 0,-55,0)
        #Draw outer ring
        ring_step = 10
        for i in range(10,60,ring_step):
            bounds = QRectF(-i, -i, i * 2, i * 2)
            painter.drawEllipse(bounds)
        painter.restore()

    def drawKnob(self,painter):
        painter.setBrush(self.knobColor)
        #print(self.movingOffset)
        if self.grabCenter:
            knob = QRectF(-self.stickRad, -self.stickRad,
                           self.stickRad*2, self.stickRad*2).translated(self.movingOffset)
        knob = QRectF(-self.stickRad, -self.stickRad,
                       self.stickRad*2, self.stickRad*2).translated(self._center())

        painter.drawEllipse(self._centerEllipse())
        # painter.restore()

    def _centerEllipse(self):
        if self.grabCenter:
            return QRectF(-self.stickRad, -self.stickRad,
                           self.stickRad*2, self.stickRad*2).translated(self.movingOffset)
        return QRectF(-self.stickRad, -self.stickRad,
                       self.stickRad*2, self.stickRad*2).translated(self._center())

    def _center(self):
        return QPointF(self.width()/2, self.height()/2)

    def _boundJoystick(self, point):
        #print(point)
        limitLine = QLineF(self._center(), point)
        if (limitLine.length() > self.__maxDistance*self.scale):
            limitLine.setLength(self.__maxDistance*self.scale)
        return limitLine.p2()

    def joystickDirection(self):
        if not self.grabCenter:
            joy_val = {
                "az_rate":0,
                "el_rate":0
            }
        else:
            outer_ring = self.__maxDistance * self.scale
            normVector = QLineF(self._center(), self.movingOffset)
            currentDistance = normVector.length()
            percentDistance = currentDistance / outer_ring
            angle = normVector.angle()
            x = np.cos(angle*DEG2RAD)
            y = np.sin(angle*DEG2RAD)
            az_rate = round(x * self._az_rate_max*percentDistance)
            el_rate = round(y * self._el_rate_max*percentDistance)
            if abs(az_rate) < self._az_dead_band:
                az_rate = 0
            if abs(el_rate) < self._el_dead_band:
                el_rate = 0
            joy_val = {
                "az_rate":az_rate,
                "el_rate":el_rate
            }
        return(joy_val)

    def mousePressEvent(self, ev):
        self.grabCenter = self._centerEllipse().contains(ev.pos())
        return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, event):
        self.grabCenter = False
        self.movingOffset = QPointF(0, 0)
        self.update()
        #print(self.joystickDirection())
        self.joy_val = self.joystickDirection()
        self.Report_Rates()

    def mouseMoveEvent(self, event):
        if self.grabCenter:
            #print("Moving")
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
        #print(self.joystickDirection())
        self.joy_val = self.joystickDirection()
        self.Report_Rates()

    def Report_Rates(self):
        az = self.joy_val['az_rate']
        el = self.joy_val['el_rate']
        theta = np.arctan2(el,  az) * RAD2DEG
        rho = np.sqrt(np.power(az,2)+np.power(el,2))
        # rho_max = np.sqrt(np.power(self._az_rate_max,2)+np.power(self._el_rate_max,2))
        rho_max = max(self._az_rate_max, self._el_rate_max)
        msg={
            "type":"autostar",
            "cmd":"slew",
            "src":"GUI_Thread",
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "az_val": self.joy_val['az_rate'],
                "el_val": self.joy_val['el_rate'],
                "az_max": self._az_rate_max,
                "el_max": self._el_rate_max,
                "theta": theta,
                "rho": rho,
                "rho_max": rho_max
            }
        }
        self.reportRates.emit(msg)
        # self.parent.q.put(self.joy_val)

    def set_az_rate_max(self, val):
        self._az_rate_max = int(val)
        print("Set Az Rate Max: {:d}".format(self._az_rate_max))

    def set_el_rate_max(self, val):
        self._el_rate_max = int(val)
        print("Set El Rate Max: {:d}".format(self._el_rate_max))

    def darken(self):
        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Background,QColor(0,0,0))
        palette.setColor(Qt.QPalette.WindowText,QColor(0,0,0))
        palette.setColor(Qt.QPalette.Text,QColor(0,255,0))
        self.setPalette(palette)
