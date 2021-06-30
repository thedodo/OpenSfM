#from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import glob
import cv2
import matplotlib.pyplot as plt
import json
import piexif
from exif import Image
import sys
import os


im_path = sys.argv[1]

folder = im_path.split('/')[0] + '/' + im_path.split('/')[1]

exif_folder = folder + '/exif'
exif_list = glob.glob(exif_folder + '/*')

f = open(exif_list[0])
data = json.load(f)

im_name = im_path.split('/')[-1].split('.')[0]
new_im_name = folder + '/localize/' + im_name + 'exif.jpg'

#dummy gps info so there is no error in sfm!
GPSInfo = {1: 'N', 2: ((36, 1), (7, 1), (5263, 100)), 3: 'W', 4: ((115, 1), (8, 1), (5789, 100)), 5: b'\x00', 6: (241175, 391), 7: ((19, 1), (8, 1), (40, 1)), 12: 'K', 13: (0, 1), 16: 'T', 17: (1017664, 4813), 23: 'T', 24: (1017664, 4813), 29: '2019:01:11', 31: (65, 1)}

with open(im_path, 'rb') as image_file:
    
    im = Image(image_file)
    
    im.make = data['make']
    im.model = data['model']
    
    im.camera = data['camera']
    
    im.GPSInfo = GPSInfo
    
    
with open(new_im_name, 'wb') as new_image_file:
     new_image_file.write(im.get_file())


with open(new_im_name, 'rb') as image_file:
    imtest = Image(image_file)
    
os.system('rm '+ im_path)

os.system('cp ' + exif_list[0] + ' ' + exif_list[0] + '1')

os.system('mv ' + exif_list[0] + '1' + ' ' + exif_folder +'/' +im_name + 'exif.jpg.exif')
