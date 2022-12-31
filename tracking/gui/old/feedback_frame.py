#!/usr/bin/env python3
#-- coding: utf-8 --

from PyQt5 import QtCore
from PyQt5 import Qt

from PyQt5.QtCore import pyqtSignal

class feedback_frame(Qt.QFrame):
    def __init__(self, parent=None, az_el = None):
        super(feedback_frame, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setFrameShape(Qt.QFrame.StyledPanel)
        self.init_widgets()
        self.connect_signals()

    def init_widgets(self):
        lbl_width = 130
        val_width = 120
        lbl_height = 14

        frame_lbl = Qt.QLabel("Feedback:")
        frame_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        frame_lbl.setStyleSheet("QLabel {font:12pt; font-weight:bold; text-decoration: underline; color:rgb(255,0,0);}")
        frame_lbl.setFixedWidth(200)
        frame_lbl.setFixedHeight(20)

        lbl = Qt.QLabel("Azimuth [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.az_deg_lbl = Qt.QLabel("XXX.XXX")
        self.az_deg_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.az_deg_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.az_deg_lbl.setFixedWidth(val_width)
        self.az_deg_lbl.setFixedHeight(lbl_height)
        az_deg_hbox = Qt.QHBoxLayout()
        az_deg_hbox.addWidget(lbl)
        az_deg_hbox.addWidget(self.az_deg_lbl)
        az_deg_hbox.addStretch(1)

        lbl = Qt.QLabel("Elevation [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.el_deg_lbl = Qt.QLabel("XXX.XXX")
        self.el_deg_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.el_deg_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.el_deg_lbl.setFixedWidth(val_width)
        self.el_deg_lbl.setFixedHeight(lbl_height)
        el_deg_hbox = Qt.QHBoxLayout()
        el_deg_hbox.addWidget(lbl)
        el_deg_hbox.addWidget(self.el_deg_lbl)
        el_deg_hbox.addStretch(1)

        lbl = Qt.QLabel("Azimuth [DMS]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.az_dms_lbl = Qt.QLabel("DDD\u00b0 MM\' SS.AAAA\"")
        self.az_dms_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.az_dms_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.az_dms_lbl.setFixedWidth(val_width)
        self.az_dms_lbl.setFixedHeight(lbl_height)
        az_dms_hbox = Qt.QHBoxLayout()
        az_dms_hbox.addWidget(lbl)
        az_dms_hbox.addWidget(self.az_dms_lbl)
        az_dms_hbox.addStretch(1)

        lbl = Qt.QLabel("Elevation [DMS]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.el_dms_lbl = Qt.QLabel("DDD\u00b0 MM\' SS.AAAA\"")
        self.el_dms_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.el_dms_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.el_dms_lbl.setFixedWidth(val_width)
        self.el_dms_lbl.setFixedHeight(lbl_height)
        el_dms_hbox = Qt.QHBoxLayout()
        el_dms_hbox.addWidget(lbl)
        el_dms_hbox.addWidget(self.el_dms_lbl)
        el_dms_hbox.addStretch(1)

        lbl = Qt.QLabel("Right Acension [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.ra_deg_lbl = Qt.QLabel("XXX.XXX")
        self.ra_deg_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.ra_deg_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.ra_deg_lbl.setFixedWidth(val_width)
        self.ra_deg_lbl.setFixedHeight(lbl_height)
        ra_deg_hbox = Qt.QHBoxLayout()
        ra_deg_hbox.addWidget(lbl)
        ra_deg_hbox.addWidget(self.ra_deg_lbl)
        ra_deg_hbox.addStretch(1)

        lbl = Qt.QLabel("Declination [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.dec_deg_lbl = Qt.QLabel("XXX.XXX")
        self.dec_deg_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.dec_deg_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.dec_deg_lbl.setFixedWidth(val_width)
        self.dec_deg_lbl.setFixedHeight(lbl_height)
        dec_deg_hbox = Qt.QHBoxLayout()
        dec_deg_hbox.addWidget(lbl)
        dec_deg_hbox.addWidget(self.dec_deg_lbl)
        dec_deg_hbox.addStretch(1)

        lbl = Qt.QLabel("GoTo In Progress:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.gtipLabel = Qt.QLabel("False")
        self.gtipLabel.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.gtipLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.gtipLabel.setFixedWidth(val_width)
        self.gtipLabel.setFixedHeight(lbl_height)
        gtip_hbox = Qt.QHBoxLayout()
        gtip_hbox.addWidget(lbl)
        gtip_hbox.addWidget(self.gtipLabel)
        gtip_hbox.addStretch(1)

        lbl = Qt.QLabel("Tracking Mode:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.trackModeLabel = Qt.QLabel("0")
        self.trackModeLabel.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.trackModeLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.trackModeLabel.setFixedWidth(val_width)
        self.trackModeLabel.setFixedHeight(lbl_height)
        track_hbox = Qt.QHBoxLayout()
        track_hbox.addWidget(lbl)
        track_hbox.addWidget(self.trackModeLabel)
        track_hbox.addStretch(1)

        lbl = Qt.QLabel("Model:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.modelLabel = Qt.QLabel("Nexstar 8SE")
        self.modelLabel.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.modelLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.modelLabel.setFixedWidth(val_width)
        self.modelLabel.setFixedHeight(lbl_height)
        model_hbox = Qt.QHBoxLayout()
        model_hbox.addWidget(lbl)
        model_hbox.addWidget(self.modelLabel)
        model_hbox.addStretch(1)

        lbl = Qt.QLabel("Tracking Mode:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.trackModeLabel = Qt.QLabel("Alt/Az")
        self.trackModeLabel.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.trackModeLabel.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.trackModeLabel.setFixedWidth(val_width)
        self.trackModeLabel.setFixedHeight(lbl_height)
        mode_hbox = Qt.QHBoxLayout()
        mode_hbox.addWidget(lbl)
        mode_hbox.addWidget(self.trackModeLabel)
        mode_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        vbox.addWidget(frame_lbl)
        vbox.addLayout(az_deg_hbox)
        vbox.addLayout(az_dms_hbox)
        vbox.addLayout(el_deg_hbox)
        vbox.addLayout(el_dms_hbox)
        #vbox.addLayout(ra_deg_hbox)
        #vbox.addLayout(dec_deg_hbox)
        vbox.addLayout(gtip_hbox)
        vbox.addLayout(model_hbox)
        vbox.addLayout(mode_hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)


    def connect_signals(self):
        pass

    def update_az_el(self, az, el):
        self.az_deg_lbl.setText("{:3.9f}".format(az))
        self.el_deg_lbl.setText("{:3.9f}".format(el))
        az_mnt,az_sec = divmod(az*3600,60)
        az_deg,az_mnt = divmod(az_mnt,60)
        self.az_dms_lbl.setText("{:03d}\u00b0 {:02d}\' {:02.6f}\"".format(int(az_deg), int(az_mnt), az_sec))
        el_mnt,el_sec = divmod(el*3600,60)
        el_deg,el_mnt = divmod(el_mnt,60)
        self.el_dms_lbl.setText("{:03d}\u00b0 {:02d}\' {:02.6f}\"".format(int(el_deg), int(el_mnt), el_sec))

    def update_ra_dec(self, ra, dec):
        self.ra_deg_lbl.setText("{:3.9f}".format(ra))
        self.dec_deg_lbl.setText("{:3.9f}".format(dec))

    def update_track_mode(self, tm):
        if tm == 0:
            self.trackModeLabel.setText("OFF")
        elif tm == 1:
            self.trackModeLabel.setText("ALT_AZ")
        elif tm == 2:
            self.trackModeLabel.setText("EQ_NORTH")
        elif tm == 3:
            self.trackModeLabel.setText("EQ_SOUTH")

    def update_gtip(self, gtip):
        self.gtipLabel.setText(str(gtip))

    def update_model(self, model):
        if model == 1:
            self.modelLabel.setText("gps_series")
        elif model == 3:
            self.modelLabel.setText("i_series")
        elif model == 4:
            self.modelLabel.setText("i_series_se")
        elif model == 5:
            self.modelLabel.setText("cge")
        elif model == 6:
            self.modelLabel.setText("advanced_gt")
        elif model == 7:
            self.modelLabel.setText("slt")
        elif model == 9:
            self.modelLabel.setText("cpc")
        elif model == 10:
            self.modelLabel.setText("gt")
        elif model == 11:
            self.modelLabel.setText("se45")
        elif model == 12:
            self.modelLabel.setText("se68")
        elif model == 15:
            self.modelLabel.setText("lcm")

    def button_clicked(self):
        sender = self.sender()
        self.parent.increment_target_angle(self.az_el,float(sender.text()))
