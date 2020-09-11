#!/usr/bin/python
#-*- coding:utf-8 -*-
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import glob
import cv2
import matplotlib.pyplot as plt
import numpy as np

import os
import piexif
from fractions import Fraction
import sys

#Ordner mit Bildern sowie einem CVS file mit den GPS Koordinaten

if len (sys.argv) != 2 :
    print("Usage: python add_gps2jpg.py folder")
    sys.exit (1)

folder = sys.argv[1]
im_list = glob.glob(folder + '/*.jpg')
gps_file = glob.glob(folder + '/*.csv')
#print(gps_file)
#print(im_list)

class ImageMetaData(object):
    '''
    Extract the exif data from any image. Data includes GPS coordinates, 
    Focal Length, Manufacture, and more.
    '''
    exif_data = None
    image = None

    def __init__(self, img_path):
        self.image = Image.open(img_path)
        #print(self.image._getexif())
        self.get_exif_data()
        super(ImageMetaData, self).__init__()

    def get_exif_data(self):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        exif_data = {}
        info = self.image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
        self.exif_data = exif_data
        return exif_data

    def get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None

    def convert_to_degress(self, value):

        """Helper function to convert the GPS coordinates 
        stored in the EXIF to degress in float format"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_lat_lng(self):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lng = None
        exif_data = self.get_exif_data()
        #print(exif_data)
        if "GPSInfo" in exif_data:      
            gps_info = exif_data["GPSInfo"]
            gps_latitude = self.get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = self.get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = self.get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = self.get_if_exist(gps_info, 'GPSLongitudeRef')
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self.convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat = 0 - lat
                lng = self.convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lng = 0 - lng
        return lat, lng
    

f = open(gps_file[0], "r")

latlong = f.read()

lines = latlong.split('\n')
lines = [string for string in lines if string != ""]


latlong = []
im_names = []
for el in range(len(lines)):
    latlong.append(lines[el].split('.jpg')[-1])
    curname = folder + '/' +lines[el].split(',')[0]
    im_names.append(curname)
    
  
#lat
print(latlong[1].split(',')[2])
#long
print(latlong[1].split(',')[1])

#für Visualisierung, z.B. mit Mapbox!
text_file = open(folder + "gps_coord.txt", "w")
n = text_file.write('latitude,longitude\n')

latlng_list = []
for i in range(len(latlong)):

  #lat
  s_lat = latlong[i].split(',')[2]
  #long
  s_long = latlong[i].split(',')[1]

  str_latlong = str(s_long) + ',' + str(s_lat) + '\n'

  text_file.write(str_latlong)

text_file.close()


def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)
    
    
    
#print(len(latlong))
#print(len(im_names))

for i in range(len(im_names)):

  #lat
  #can be none, check for that!!!
  if(latlong[i].split(',')[1] == 'None'):
      continue
  cur_lat = float(latlong[i].split(',')[1])
  #long
  if(latlong[i].split(',')[1] == 'None'):
      continue  
  cur_long = float(latlong[i].split(',')[2])
  cur_im = im_names[i]
  print("set gps location for: ",cur_im)

  set_gps_location(cur_im, cur_lat, cur_long, 0.0)