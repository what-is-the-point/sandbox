#!/usr/bin/env python
from math import *
import string
import time
import sys
import csv
import os
from datetime import datetime as date
import numpy as np

deg2rad = pi / 180.0
rad2deg = 180.0 / pi
c       = float(299792458)  #[m/s], speed of light
R_e     = 6378.137 				#Earth Radius, in kilometers
e_e     = 0.081819221456	    #Eccentricity of Earth

track_msg = {
    "icao": None,      # MLAT, MSG, CLK, STA, AIR, ID, SEL
    "callsign":'',       # transmission type
    "azimuth":0.0,    # String. Database session record number.
    "elevation":0.0,   # String. Database aircraft record number.
    "range":0.0,     # String. 24-bit ICACO ID, in hex.
    "geo_alt":0.0,     # String. Database flight record number.
    "baro_alt":0.0,
    "vert_rate":0.0,
    "speed":0.0,# String. Date the message was generated.
    "track":0.0,# String. Time the message was generated.
    "msg_src":'',   # String. Date the message was logged.
    "msg_cnt":0,    # String. Time the message was logged.
    "date_last":'', #last date stamp
    "time_last":'', #last time stamp
    "age":0.0, #seconds since last time stamp
}
#--Range Calculations Functions------
def LLH_To_ECEF(lat, lon, h):
	#INPUT:
	#	h   - height above ellipsoid (MSL), km
	#	lat - geodetic latitude, in radians
	#	lon - longitude, in radians
    C_e = R_e / sqrt(1 - pow(e_e, 2) * pow(sin(lat),2))
    S_e = C_e * (1 - pow(e_e, 2))
    r_i = (C_e + h) * cos(lat) * cos(lon)
    r_j = (C_e + h) * cos(lat) * sin(lon)
    r_k = (S_e + h) * sin(lat)
    return r_i, r_j, r_k

def RAZEL(lat1, lon1, h1, lat2, lon2, h2):
	#Calculates Range, Azimuth, Elevation in SEZ coordinate frame from SITE to UAV
	#INPUT:
	# lat1, lon1, h1 - Site Location
	# lat2, lon2, h2 - UAV location
    # lats and lons in degrees
    # h in km
	#OUTPUT:
	# Slant Range, Azimuth, Elevation

    lat1 = lat1 * deg2rad
    lon1 = lon1 * deg2rad
    lat2 = lat2 * deg2rad
    lon2 = lon2 * deg2rad

    r_site   = np.array(LLH_To_ECEF(lat1, lon1, h1))
    r_uav    = np.array(LLH_To_ECEF(lat2, lon2, h2))
    rho_ecef = r_uav - r_site

    ECEF_2_SEZ_ROT = np.array([[sin(lat1) * cos(lon1), sin(lat1) * sin(lon1), -1 * cos(lat1)],
                               [-1 * sin(lon1)       , cos(lon1)            , 0             ],
                               [cos(lat1) * cos(lon1), cos(lat1) * sin(lon1), sin(lat1)     ]])

    rho_sez = np.dot(ECEF_2_SEZ_ROT ,rho_ecef)
    rho_mag = np.linalg.norm(rho_sez)
    el = asin(rho_sez[2]/rho_mag) * rad2deg
    az_asin = asin(rho_sez[1]/sqrt(pow(rho_sez[0],2)+pow(rho_sez[1], 2))) * rad2deg
    az_acos = acos(-1 * rho_sez[0]/sqrt(pow(rho_sez[0],2)+pow(rho_sez[1], 2))) * rad2deg
    #print az_asin, az_acos
    #Perform Quadrant Check:
    if (az_asin >= 0) and (az_acos >= 0): az = az_acos# First or Fourth Quadrant
    else: az = 360 - az_acos# Second or Third Quadrant
    #This is the Azimuth From the TARGET to the UAV
    #Must convert to Back Azimuth:
    back_az = az + 180
    if back_az >= 360:  back_az = back_az - 360
    #print az, back_az
    # rho_mag in kilometers, range to target
    # back_az in degrees, 0 to 360
    # el in degrees, negative = down tilt, positive = up tilt
    razel = {
        "rho": rho_mag,
        "az":az,
        "el":el
    }
    # return rho_mag, az, el
    return razel
