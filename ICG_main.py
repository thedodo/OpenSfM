#created by Dominik Hirner and Chetan Kumar 09.09.2020
import os
import argparse
import sys
import glob
import random
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

parser = argparse.ArgumentParser(description='ICG main function für SV4VI Projekt. (Getestet auf Ubuntu 18.04 LTS)')

parser.add_argument('--build', help='Sollte zur Einrichtung der Software ausgeführt werden.', action="store_true")
parser.add_argument('--test', help='Test ob die Einrichtung funktioniert hat.', action="store_true")
parser.add_argument('--test_loc', help = 'Testet Lokalisierung uvm. Für eine genaue Übersicht: https://github.com/thedodo/OpenSfM.git', action="store_true")

args = parser.parse_args()






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


if args.build:
    os.chdir('ICG/')
    os.system('./install_opensfm.sh > ../log_install.txt')
    os.chdir('../')
    cwd = os.getcwd() 
    os.system('./ICG/expand_bashrc.sh')
    #print('Building software....')
    print('.............Fertig! Der output wurde in log.txt geschrieben.')
    
    
if args.test:
    os.system('./ICG/test_install.sh > log_test.txt')
    print('.....Fertig!')
    #file to check!
    file_path = './data/lund/undistorted/depthmaps/merged.ply'
    # check if size of file is 0
    if os.stat(file_path).st_size != 0:
        print('Die Einrichtung hat funktioniert!')
    if os.stat(file_path).st_size == 0:
        print('Leider scheint etwas schief gelaufen zu sein. Bitte kontrolliere die log-files!')


if args.test_loc:
    
  #  os.system('mkdir data/inffeldgasse')
  #  os.chdir('data/inffeldgasse')
 #   os.system('mkdir images')
  #  os.chdir('images/')
  #  os.system('wget https://cloud.tugraz.at/index.php/s/7HYz9iz3fcr43bH/download')
  #  os.system('unzip download')
  #  os.chdir('../../../')
    
  #  os.system('python3 ICG/add_gps2jpg.py ./data/inffeldgasse/images/')
    
    
    im_list = glob.glob('./data/inffeldgasse/images/*.jpg')
    
  #  meta_data =  ImageMetaData(random.choice(im_list))
  #  exif_data = meta_data.get_exif_data()
  #  latlng =meta_data.get_lat_lng()
 #   if(str(latlng[0]) == 'None'):
   #     print('Etwas ist schief gegangen!')
   #     exit()
  #  else:
   #     print('GPS tags erfolgreich')
   #     str_latlong = str(latlng[0]) + ',' + str(latlng[1]) + '\n'
   #     print(str_latlong)
   
    #os.system('./bin/opensfm_run_all data/inffeldgasse > log_test_inffeld.txt')
    file_path = './data/inffeldgasse/undistorted/depthmaps/merged.ply'
    # check if size of file is 0
    if os.stat(file_path).st_size == 0:
        print('Leider scheint etwas schief gelaufen zu sein. Bitte kontrolliere die log-files!')
        exit()
    
    
    #os.system('python3 ICG/georeference_ply.py --opensfm_data_path data/inffeldgasse --plyfile_path data/inffeldgasse/undistorted/depthmaps/merged.ply')
    #os.system('mkdir ./data/inffeldgasse/localize/')
    #rand_to_loc = random.choice(im_list)
    #rand_name = rand_to_loc.split('/')[-1]
    #os.system('cp '+ rand_to_loc + ' ./data/inffeldgasse/localize/' + rand_name)
    #os.system('bin/localize data/inffeldgasse')
    #os.system('python3 ICG/gps_to_name.py data/inffeldgasse/localize/localize.json ' + rand_name)
    
    os.system('python3 ICG/flatten_pointcloud.py data/inffeldgasse')
    
    
