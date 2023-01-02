#!/usr/bin/env python3
#-- coding: utf-8 --
import datetime
from PyQt5 import QtCore
from PyQt5 import Qt
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import pyqtSignal

class ObserverLocationFrame(QGroupBox):
    locationUpdateSignal = pyqtSignal(dict)

    def __init__(self, cfg=None, parent=None):
        super(ObserverLocationFrame, self).__init__()
        self.parent = parent
        self.cfg=cfg
        self.setTitle(self.cfg['name'])
        self.setContentsMargins(1,10,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.setMinimumHeight(200)

        self.lat = self.cfg['lat']
        self.lon = self.cfg['lon']
        self.alt = self.cfg['alt']

        self.initUI()

    def initUI(self):
        # self.setFrameShape(Qt.QFrame.StyledPanel)
        self.setMinimumSize(50, 50)
        # self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.init_widgets()
        self.connect_signals()

    def connect_signals(self):
        self.lat_le.editingFinished.connect(self._lat_edit)
        self.lon_le.editingFinished.connect(self._lon_edit)
        self.alt_le.editingFinished.connect(self._alt_edit)
        self.update_loc_button.clicked.connect(self._update_location)

    def _lat_edit(self):
        self.lat = float(self.lat_le.text())

    def _lon_edit(self):
        self.lon = float(self.lon_le.text())

    def _alt_edit(self):
        self.alt = float(self.alt_le.text())

    def _update_location(self):
        msg={
            "type":"CTL",
            "cmd":"location",
            "src":"GUI.ADSB",
            "dest": 'MAIN',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "lat": self.lat,
                "lon": self.lon,
                "alt": self.alt
            }
        }
        self.locationUpdateSignal.emit(msg)

    def init_widgets(self):
        lbl_width = 65
        val_width = 100
        lbl_height = 12
        btn_height = 20

        label = Qt.QLabel('Lat [deg]:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.lat_le = Qt.QLineEdit()
        self.lat_le.setText("{:2.7f}".format(self.lat))
        self.lat_le.setInputMask("00.0000000;")
        lat_validator = Qt.QDoubleValidator()
        lat_validator.setRange(-180.0, 180.0)
        self.lat_le.setValidator(lat_validator)
        self.lat_le.setEchoMode(Qt.QLineEdit.Normal)
        self.lat_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        # self.lat_le.setMaxLength(lbl_width)
        self.lat_le.setFixedHeight(20)
        self.lat_le.setFixedWidth(val_width)
        lat_hbox = Qt.QHBoxLayout()
        lat_hbox.addWidget(label)
        lat_hbox.addWidget(self.lat_le)

        label = Qt.QLabel('Lon [deg]:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.lon_le = Qt.QLineEdit()
        self.lon_le.setText("{:3.7f}".format(self.lon))
        self.lon_le.setInputMask("000.0000000;")
        lon_validator = Qt.QDoubleValidator()
        lon_validator.setRange(-180.0, 180.0)
        self.lon_le.setValidator(lon_validator)
        self.lon_le.setEchoMode(Qt.QLineEdit.Normal)
        self.lon_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        # self.lon_le.setMaxLength(5)
        self.lon_le.setFixedWidth(val_width)
        self.lon_le.setFixedHeight(20)
        lon_hbox = Qt.QHBoxLayout()
        lon_hbox.addWidget(label)
        lon_hbox.addWidget(self.lon_le)

        label = Qt.QLabel('Alt [m]:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.alt_le = Qt.QLineEdit()
        self.alt_le.setText("{:3.7f}".format(self.alt))
        self.alt_le.setInputMask("000.0000000;")
        alt_validator = Qt.QDoubleValidator()
        alt_validator.setRange(-100.0, 45000)
        self.alt_le.setValidator(alt_validator)
        self.alt_le.setEchoMode(Qt.QLineEdit.Normal)
        self.alt_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        # self.lon_le.setMaxLength(5)
        self.alt_le.setFixedWidth(val_width)
        self.alt_le.setFixedHeight(20)
        alt_hbox = Qt.QHBoxLayout()
        alt_hbox.addWidget(label)
        alt_hbox.addWidget(self.alt_le)

        self.update_loc_button = Qt.QPushButton("Update Location")
        self.update_loc_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.update_loc_button.setFixedWidth(120)

        btn_hbox = Qt.QHBoxLayout()
        # btn_hbox.addStretch(1)
        btn_hbox.addWidget(self.update_loc_button)
        btn_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        # vbox.addWidget(frame_lbl)
        vbox.addLayout(lat_hbox)
        vbox.addLayout(lon_hbox)
        vbox.addLayout(alt_hbox)
        vbox.setSpacing(2)
        vbox.addStretch(1)
        vbox.addLayout(btn_hbox)
        self.setLayout(vbox)

class ADSBTargetSelectFrame(QGroupBox):
    ICAOTargetSignal = pyqtSignal(dict)
    def __init__(self, target="abcdef", name = 'Target ICAO', parent=None):
        super(ADSBTargetSelectFrame, self).__init__()
        self.parent = parent
        self.setTitle(name)
        self.target_icao = target.upper()
        self.setContentsMargins(1,10,1,1)
        self.initUI()

    def initUI(self):
        self.init_widgets()
        self.connect_signals()

    def connect_signals(self):
        self.icao_le.editingFinished.connect(self._icao_edit)
        self.target_button.clicked.connect(self._select_target)
        self.cancel_button.clicked.connect(self._cancel_target)

    def _icao_edit(self):
        self.target_icao = self.icao_le.text().upper()

    def _select_target(self):
        msg={
            "type":"CTL",
            "cmd":"select_icao",
            "src":"GUI.ADSB",
            "dest":'ADSB.MLAT',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "icao": self.target_icao
            }
        }
        self.ICAOTargetSignal.emit(msg)

    def _cancel_target(self):
        msg={
            "type":"CTL",
            "cmd":"cancel_icao",
            "src":"GUI.ADSB",
            "dest":'ADSB',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        }
        self.ICAOTargetSignal.emit(msg)

    def init_widgets(self):
        lbl_width = 75
        val_width = 75
        lbl_height = 14

        label = Qt.QLabel('Target ICAO:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.icao_le = Qt.QLineEdit()
        self.icao_le.setText(self.target_icao)
        # self.icao_le.setInputMask("000.000.000.000;")
        self.icao_le.setEchoMode(Qt.QLineEdit.Normal)
        self.icao_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.icao_le.setMaxLength(15)
        self.icao_le.setFixedHeight(20)
        self.icao_le.setFixedWidth(val_width)
        icao_hbox = Qt.QHBoxLayout()
        icao_hbox.addWidget(label)
        icao_hbox.addWidget(self.icao_le)
        icao_hbox.addStretch(1)

        self.target_button = Qt.QPushButton("Select")
        self.target_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.target_button.setFixedHeight(20)
        # self.target_button.setFixedWidth(100)

        self.cancel_button = Qt.QPushButton("Cancel")
        self.cancel_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        self.cancel_button.setFixedHeight(20)
        # self.cancel_button.setFixedWidth(100)
        btn_hbox = Qt.QHBoxLayout()
        btn_hbox.addStretch(1)
        btn_hbox.addWidget(self.target_button)
        btn_hbox.addWidget(self.cancel_button)
        btn_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        # vbox.addWidget(frame_lbl)
        vbox.addLayout(icao_hbox)
        vbox.addLayout(btn_hbox)
        self.setLayout(vbox)

class ADSBFeedbackFrame(QGroupBox):
    def __init__(self, name = None, parent=None):
        super(ADSBFeedbackFrame, self).__init__()
        self.parent = parent
        self.setTitle(name)
        self.setContentsMargins(1,10,1,1)
        self.trk_msg = None
        self.initUI()

    def initUI(self):
        self.init_widgets()
        # self.connect_signals()
        self.clock_timer = QtCore.QTimer(self)
        self.clock_timer.setInterval(10)
        self.clock_timer.timeout.connect(self._update_clock_time)
        self.clock_timer.start()

    def _update_clock_time(self):
        now_ts = datetime.datetime.utcnow()
        now_str = now_ts.strftime("%H:%M:%S.%fZ")
        self.cur_time_lbl.setText("{:s}".format(now_str))
        if self.trk_msg != None:
            last_t_str = "{:s} {:s}".format(self.trk_msg['date_last'],
                                            self.trk_msg['time_last'])
            last_ts = datetime.datetime.strptime(last_t_str,
                                                 "%Y-%m-%d %H:%M:%S.%fZ")
            delta_t = (now_ts - last_ts).total_seconds() #convert to UTC from Eastern
            self.age_lbl.setText("{:2.3f}".format(delta_t))
            if (self.trk_msg['pos_date'] != None) and (self.trk_msg['pos_time'] != None):
                pos_t_str = "{:s} {:s}".format(self.trk_msg['pos_date'],
                                               self.trk_msg['pos_time'])
                pos_ts = datetime.datetime.strptime(pos_t_str,
                                                    "%Y-%m-%d %H:%M:%S.%fZ")
                pos_delta_t = (now_ts - pos_ts).total_seconds() #convert to UTC from Eastern
                self.pos_age_lbl.setText("{:2.3f}".format(pos_delta_t))

    def update_data(self, msg):
        # print('adsbfeedbackframe', msg)
        self.trk_msg = msg
        self.icao_lbl.setText("{:s}".format(msg['icao']))
        self.call_lbl.setText("{:s}".format(msg['callsign']))
        self.az_lbl.setText("{:3.2f} / {:2.3f}".format(msg['azimuth'], msg['az_rate']))
        self.el_lbl.setText("{:2.2f} / {:2.3f}".format(msg['elevation'], msg['el_rate']))
        self.range_lbl.setText("{:3.2f} / {:2.3f}".format(msg['range'], msg['range_rate']))
        self.geo_alt_lbl.setText("{:6.1f}".format(msg['geo_alt']))
        self.baro_alt_lbl.setText("{:6.1f}".format(msg['baro_alt']))
        self.vert_rate_lbl.setText("{:3.1f}".format(msg['vert_rate']))
        self.spd_kts_lbl.setText("{:3.1f}".format(msg['speed']))
        self.track_lbl.setText("{:3.1f}".format(msg['track']))
        self.source_lbl.setText("{:s}".format(msg['msg_src']))
        self.msg_cnt_lbl.setText("{:d}".format(msg['msg_cnt']))
        self.date_lbl.setText("{:s}".format(msg['date_last']))
        self.last_time_lbl.setText("{:s}".format(msg['time_last']))

    def init_widgets(self):
        lbl_width = 115
        val_width = 110
        lbl_height = 14

        lbl = Qt.QLabel("ICAO:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.icao_lbl = Qt.QLabel("XXX.XXX")
        self.icao_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.icao_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.icao_lbl.setFixedWidth(val_width)
        self.icao_lbl.setFixedHeight(lbl_height)
        icao_hbox = Qt.QHBoxLayout()
        icao_hbox.addWidget(lbl)
        icao_hbox.addWidget(self.icao_lbl)
        icao_hbox.addStretch(1)

        lbl = Qt.QLabel("Callsign:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.call_lbl = Qt.QLabel("XXX.XXX")
        self.call_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.call_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.call_lbl.setFixedWidth(val_width)
        self.call_lbl.setFixedHeight(lbl_height)
        call_hbox = Qt.QHBoxLayout()
        call_hbox.addWidget(lbl)
        call_hbox.addWidget(self.call_lbl)
        call_hbox.addStretch(1)

        lbl = Qt.QLabel("Azimuth [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.az_lbl = Qt.QLabel("XXX.XXX")
        self.az_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.az_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.az_lbl.setFixedWidth(val_width)
        self.az_lbl.setFixedHeight(lbl_height)
        az_deg_hbox = Qt.QHBoxLayout()
        az_deg_hbox.addWidget(lbl)
        az_deg_hbox.addWidget(self.az_lbl)
        az_deg_hbox.addStretch(1)

        lbl = Qt.QLabel("Elevation [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.el_lbl = Qt.QLabel("XXX.XXX")
        self.el_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.el_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.el_lbl.setFixedWidth(val_width)
        self.el_lbl.setFixedHeight(lbl_height)
        el_deg_hbox = Qt.QHBoxLayout()
        el_deg_hbox.addWidget(lbl)
        el_deg_hbox.addWidget(self.el_lbl)
        el_deg_hbox.addStretch(1)

        lbl = Qt.QLabel("Range [km]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.range_lbl = Qt.QLabel("XXX.XXX")
        self.range_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.range_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.range_lbl.setFixedWidth(val_width)
        self.range_lbl.setFixedHeight(lbl_height)
        range_hbox = Qt.QHBoxLayout()
        range_hbox.addWidget(lbl)
        range_hbox.addWidget(self.range_lbl)
        range_hbox.addStretch(1)

        lbl = Qt.QLabel("Position Age [s]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.pos_age_lbl = Qt.QLabel("XXX.XXX")
        self.pos_age_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.pos_age_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.pos_age_lbl.setFixedWidth(val_width)
        self.pos_age_lbl.setFixedHeight(lbl_height)
        pos_age_hbox = Qt.QHBoxLayout()
        pos_age_hbox.addWidget(lbl)
        pos_age_hbox.addWidget(self.pos_age_lbl)
        pos_age_hbox.addStretch(1)

        lbl = Qt.QLabel("Geo Altitude [ft]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.geo_alt_lbl = Qt.QLabel("XXX.XXX")
        self.geo_alt_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.geo_alt_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.geo_alt_lbl.setFixedWidth(val_width)
        self.geo_alt_lbl.setFixedHeight(lbl_height)
        geo_alt_hbox = Qt.QHBoxLayout()
        geo_alt_hbox.addWidget(lbl)
        geo_alt_hbox.addWidget(self.geo_alt_lbl)
        geo_alt_hbox.addStretch(1)

        lbl = Qt.QLabel("Baro Altitude [ft]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.baro_alt_lbl = Qt.QLabel("XXX.XXX")
        self.baro_alt_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.baro_alt_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.baro_alt_lbl.setFixedWidth(val_width)
        self.baro_alt_lbl.setFixedHeight(lbl_height)
        baro_alt_hbox = Qt.QHBoxLayout()
        baro_alt_hbox.addWidget(lbl)
        baro_alt_hbox.addWidget(self.baro_alt_lbl)
        baro_alt_hbox.addStretch(1)

        lbl = Qt.QLabel("Vert Rate [ft/min]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.vert_rate_lbl = Qt.QLabel("XXX.XXX")
        self.vert_rate_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.vert_rate_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.vert_rate_lbl.setFixedWidth(val_width)
        self.vert_rate_lbl.setFixedHeight(lbl_height)
        vert_rate_hbox = Qt.QHBoxLayout()
        vert_rate_hbox.addWidget(lbl)
        vert_rate_hbox.addWidget(self.vert_rate_lbl)
        vert_rate_hbox.addStretch(1)

        lbl = Qt.QLabel("Speed [knots]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.spd_kts_lbl = Qt.QLabel("XXX.XXX")
        self.spd_kts_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.spd_kts_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.spd_kts_lbl.setFixedWidth(val_width)
        self.spd_kts_lbl.setFixedHeight(lbl_height)
        spd_kts_hbox = Qt.QHBoxLayout()
        spd_kts_hbox.addWidget(lbl)
        spd_kts_hbox.addWidget(self.spd_kts_lbl)
        spd_kts_hbox.addStretch(1)

        lbl = Qt.QLabel("Track [deg]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.track_lbl = Qt.QLabel("XXX.XXX")
        self.track_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.track_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.track_lbl.setFixedWidth(val_width)
        self.track_lbl.setFixedHeight(lbl_height)
        track_hbox = Qt.QHBoxLayout()
        track_hbox.addWidget(lbl)
        track_hbox.addWidget(self.track_lbl)
        track_hbox.addStretch(1)

        lbl = Qt.QLabel("Message Source:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.source_lbl = Qt.QLabel("ADSB/MLAT")
        self.source_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.source_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.source_lbl.setFixedWidth(val_width)
        self.source_lbl.setFixedHeight(lbl_height)
        source_hbox = Qt.QHBoxLayout()
        source_hbox.addWidget(lbl)
        source_hbox.addWidget(self.source_lbl)
        source_hbox.addStretch(1)

        lbl = Qt.QLabel("Message Count:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.msg_cnt_lbl = Qt.QLabel("XXX.XXX")
        self.msg_cnt_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.msg_cnt_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.msg_cnt_lbl.setFixedWidth(val_width)
        self.msg_cnt_lbl.setFixedHeight(lbl_height)
        msg_cnt_hbox = Qt.QHBoxLayout()
        msg_cnt_hbox.addWidget(lbl)
        msg_cnt_hbox.addWidget(self.msg_cnt_lbl)
        msg_cnt_hbox.addStretch(1)

        lbl = Qt.QLabel("Last Date:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.date_lbl = Qt.QLabel("XXX.XXX")
        self.date_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.date_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.date_lbl.setFixedWidth(val_width)
        self.date_lbl.setFixedHeight(lbl_height)
        date_hbox = Qt.QHBoxLayout()
        date_hbox.addWidget(lbl)
        date_hbox.addWidget(self.date_lbl)
        date_hbox.addStretch(1)

        lbl = Qt.QLabel("Last Msg Time:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.last_time_lbl = Qt.QLabel("XXX.XXX")
        self.last_time_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.last_time_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.last_time_lbl.setFixedWidth(val_width)
        self.last_time_lbl.setFixedHeight(lbl_height)
        last_time_hbox = Qt.QHBoxLayout()
        last_time_hbox.addWidget(lbl)
        last_time_hbox.addWidget(self.last_time_lbl)
        last_time_hbox.addStretch(1)

        lbl = Qt.QLabel("Current Time:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.cur_time_lbl = Qt.QLabel("XXX.XXX")
        self.cur_time_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.cur_time_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.cur_time_lbl.setFixedWidth(val_width)
        self.cur_time_lbl.setFixedHeight(lbl_height)
        cur_time_hbox = Qt.QHBoxLayout()
        cur_time_hbox.addWidget(lbl)
        cur_time_hbox.addWidget(self.cur_time_lbl)
        cur_time_hbox.addStretch(1)

        lbl = Qt.QLabel("Last Msg Age [s]:")
        lbl.setAlignment(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        lbl.setFixedWidth(lbl_width)
        lbl.setFixedHeight(lbl_height)
        self.age_lbl = Qt.QLabel("XXX.XXX")
        self.age_lbl.setAlignment(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
        self.age_lbl.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        self.age_lbl.setFixedWidth(val_width)
        self.age_lbl.setFixedHeight(lbl_height)
        age_hbox = Qt.QHBoxLayout()
        age_hbox.addWidget(lbl)
        age_hbox.addWidget(self.age_lbl)
        age_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        vbox.addLayout(icao_hbox)
        vbox.addLayout(call_hbox)
        vbox.addLayout(az_deg_hbox)
        vbox.addLayout(el_deg_hbox)
        vbox.addLayout(range_hbox)
        vbox.addLayout(pos_age_hbox)
        vbox.addLayout(geo_alt_hbox)
        vbox.addLayout(baro_alt_hbox)
        vbox.addLayout(vert_rate_hbox)
        vbox.addLayout(spd_kts_hbox)
        vbox.addLayout(track_hbox)
        vbox.addLayout(source_hbox)
        vbox.addLayout(msg_cnt_hbox)
        # vbox.addLayout(date_hbox)
        vbox.addLayout(last_time_hbox)
        vbox.addLayout(cur_time_hbox)
        vbox.addLayout(age_hbox)
        vbox.addStretch(1)
        self.setLayout(vbox)

class ADSBConnFrame(QGroupBox):
    ADSBConnectSignal = pyqtSignal(dict)

    def __init__(self, cfg=None, parent=None):
        super(ADSBConnFrame, self).__init__()
        self.parent = parent
        self.cfg=cfg
        self.setTitle(self.cfg['name'])
        self.setContentsMargins(1,10,1,1)
        # self.setStyleSheet("QGroupBox {font: 12px; color: rgb(255,255,255)}")
        self.setMinimumHeight(200)

        self.ip        = self.cfg['ip']
        self.sbs1_port = self.cfg['sbs1_port']
        self.mlat_port = self.cfg['mlat_port']
        self.adsb_connected = False
        self.mlat_connected = False

        self.initUI()

    def initUI(self):
        # self.setFrameShape(Qt.QFrame.StyledPanel)
        self.setMinimumSize(50, 50)
        # self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.init_widgets()
        self.connect_signals()

    def connect_signals(self):
        self.ip_le.editingFinished.connect(self._ip_edit)
        self.sbs1_port_le.editingFinished.connect(self._sbs1_port_edit)
        self.mlat_port_le.editingFinished.connect(self._mlat_port_edit)
        self.adsb_connect_button.clicked.connect(self._adsb_connect)
        self.mlat_connect_button.clicked.connect(self._mlat_connect)

    def _ip_edit(self):
        self.ip = self.ip_le.text()

    def _sbs1_port_edit(self):
        self.sbs1_port = int(self.sbs1_port_le.text())

    def _mlat_port_edit(self):
        self.mlat_port = int(self.mlat_port_le.text())

    def _adsb_connect(self):
        msg={
            "type":"CTL",
            "cmd":"connect",
            "src":"GUI.ADSB",
            "dest": 'ADSB',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "ip": self.ip,
                "port": self.sbs1_port,
                "connect": (not self.adsb_connected)
            }
        }
        self.ADSBConnectSignal.emit(msg)
        # self.update_connection_state()

    def _mlat_connect(self):
        msg={
            "type":"CTL",
            "cmd":"connect",
            "src":"GUI.ADSB",
            "dest": 'MLAT',
            "params": {
                "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "ip": self.ip,
                "port": self.mlat_port,
                "connect": (not self.mlat_connected)
            }
        }
        self.ADSBConnectSignal.emit(msg)

    def update_sbs1_connection_state(self, state):
        self.adsb_connected = state
        if self.adsb_connected == True:
            self.adsb_connect_button.setText('ADSB Disconnect')
            self.conn_adsb_lbl.setText('CONNECTED')
            self.conn_adsb_lbl.setStyleSheet("QLabel {font: 12px; font-weight:bold; color:rgb(0,255,0);}")
            #self.update_timer.start()
        elif self.adsb_connected == False:
            self.adsb_connect_button.setText('ADSB Connect')
            self.conn_adsb_lbl.setText('DISCONNECTED')
            self.conn_adsb_lbl.setStyleSheet("QLabel {font: 12px; font-weight:bold; color:rgb(255,0,0);}")

    def update_mlat_connection_state(self, state):
        self.mlat_connected = state
        if self.mlat_connected == True:
            self.mlat_connect_button.setText('MLAT Disconnect')
            self.conn_mlat_lbl.setText('CONNECTED')
            self.conn_mlat_lbl.setStyleSheet("QLabel {font: 12px; font-weight:bold; color:rgb(0,255,0);}")
            #self.update_timer.start()
        elif self.mlat_connected == False:
            self.mlat_connect_button.setText('MLAT Connect')
            self.conn_mlat_lbl.setText('DISCONNECTED')
            self.conn_mlat_lbl.setStyleSheet("QLabel {font: 12px; font-weight:bold; color:rgb(255,0,0);}")

    def init_widgets(self):
        lbl_width = 85
        val_width = 100
        lbl_height = 12
        btn_height = 20

        label = Qt.QLabel('IP:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.ip_le = Qt.QLineEdit()
        self.ip_le.setText(self.cfg['ip'])
        self.ip_le.setInputMask("000.000.000.000;")
        self.ip_le.setEchoMode(Qt.QLineEdit.Normal)
        self.ip_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.ip_le.setMaxLength(15)
        self.ip_le.setFixedHeight(20)
        self.ip_le.setFixedWidth(val_width)
        ip_hbox = Qt.QHBoxLayout()
        ip_hbox.addWidget(label)
        ip_hbox.addWidget(self.ip_le)

        label = Qt.QLabel('SBS1 Port:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.sbs1_port_le = Qt.QLineEdit()
        self.sbs1_port_le.setText(str(self.cfg['sbs1_port']))
        port_validator = Qt.QIntValidator()
        port_validator.setRange(0,65535)
        self.sbs1_port_le.setValidator(port_validator)
        self.sbs1_port_le.setEchoMode(Qt.QLineEdit.Normal)
        self.sbs1_port_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.sbs1_port_le.setMaxLength(5)
        self.sbs1_port_le.setFixedWidth(val_width)
        self.sbs1_port_le.setFixedHeight(20)
        sbs1_hbox = Qt.QHBoxLayout()
        sbs1_hbox.addWidget(label)
        sbs1_hbox.addWidget(self.sbs1_port_le)

        label = Qt.QLabel('MLAT Port:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.mlat_port_le = Qt.QLineEdit()
        self.mlat_port_le.setText(str(self.cfg['mlat_port']))
        port_validator = Qt.QIntValidator()
        port_validator.setRange(0,65535)
        self.mlat_port_le.setValidator(port_validator)
        self.mlat_port_le.setEchoMode(Qt.QLineEdit.Normal)
        self.mlat_port_le.setStyleSheet("QLineEdit {font:10pt; background-color:rgb(200,75,75); color:rgb(0,0,0);}")
        self.mlat_port_le.setMaxLength(5)
        self.mlat_port_le.setFixedWidth(val_width)
        self.mlat_port_le.setFixedHeight(20)
        mlat_hbox = Qt.QHBoxLayout()
        mlat_hbox.addWidget(label)
        mlat_hbox.addWidget(self.mlat_port_le)

        # port_hbox = Qt.QHBoxLayout()
        # port_hbox.addLayout(sbs1_hbox)
        # port_hbox.addLayout(mlat_hbox)

        label = Qt.QLabel('ADSB Status:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.conn_adsb_lbl = Qt.QLabel('Disconnected')
        self.conn_adsb_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.conn_adsb_lbl.setStyleSheet("QLabel {font:10pt; font-weight:bold; color:rgb(255,0,0);}")
        self.conn_adsb_lbl.setFixedWidth(val_width)
        self.conn_adsb_lbl.setFixedHeight(20)

        adsb_conn_hbox = Qt.QHBoxLayout()
        adsb_conn_hbox.addWidget(label)
        adsb_conn_hbox.addWidget(self.conn_adsb_lbl)

        label = Qt.QLabel('MLAT Status:')
        label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel {font:10pt; color:rgb(255,0,0);}")
        label.setFixedHeight(20)
        label.setFixedWidth(lbl_width)
        self.conn_mlat_lbl = Qt.QLabel('Disconnected')
        self.conn_mlat_lbl.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.conn_mlat_lbl.setStyleSheet("QLabel {font:10pt; font-weight:bold; color:rgb(255,0,0);}")
        self.conn_mlat_lbl.setFixedWidth(val_width)
        self.conn_mlat_lbl.setFixedHeight(20)

        mlat_conn_hbox = Qt.QHBoxLayout()
        mlat_conn_hbox.addWidget(label)
        mlat_conn_hbox.addWidget(self.conn_mlat_lbl)

        self.adsb_connect_button = Qt.QPushButton("ADSB Connect")
        self.adsb_connect_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        # self.connect_button.setFixedHeight(20)
        self.adsb_connect_button.setFixedWidth(120)
        self.mlat_connect_button = Qt.QPushButton("MLAT Connect")
        self.mlat_connect_button.setStyleSheet("QPushButton {font:10pt; background-color:rgb(220,0,0);}")
        # self.connect_button.setFixedHeight(20)
        self.mlat_connect_button.setFixedWidth(120)

        adsb_btn_hbox = Qt.QHBoxLayout()
        # adsb_btn_hbox.addStretch(1)
        adsb_btn_hbox.addWidget(self.adsb_connect_button)
        # adsb_btn_hbox.addWidget(self.mlat_connect_button)
        adsb_btn_hbox.addStretch(1)

        mlat_btn_hbox = Qt.QHBoxLayout()
        # mlat_btn_hbox.addStretch(1)
        mlat_btn_hbox.addWidget(self.mlat_connect_button)
        mlat_btn_hbox.addStretch(1)

        vbox = Qt.QVBoxLayout()
        # vbox.addWidget(frame_lbl)
        vbox.addLayout(ip_hbox)
        vbox.addLayout(sbs1_hbox)
        vbox.addLayout(mlat_hbox)
        vbox.addLayout(adsb_conn_hbox)
        vbox.addLayout(mlat_conn_hbox)
        vbox.setSpacing(2)
        vbox.addStretch(1)
        vbox.addLayout(adsb_btn_hbox)
        vbox.addLayout(mlat_btn_hbox)
        self.setLayout(vbox)
