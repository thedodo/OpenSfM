import copy
import logging
import time
import os
import glob

from opensfm import dataset
from opensfm import exif


class Command:
    name = 'write_gps'
    help = "Write GPS from CSV to EXIF files"

    def add_arguments(self, parser):
        parser.add_argument('dataset', help='dataset to process')

    def run(self, args):
        data = dataset.DataSet(args.dataset)
        #root: data.data_path
        csv = os.path.join(data.data_path, data.data_path.split('/')[-2])
        csv = csv + '.csv'
        if(not (os.path.exists(csv))):
            print('csv not found!')
            return
        #read csv data
        f = open(csv, "r")
        for line in f:
            name = line.split(',')[0]
            lat = line.split(',')[1]
            lon = line.split(',')[2].rstrip("\n")
            
            gps = {}
            gps['latitude'] = float(lat)
            gps['longitude'] = float(lon)
            gps['altitude'] = 5.0
    
            exif_data = data.load_exif(name)
            exif_data['gps'] = gps
            
            data.save_exif(name, exif_data)
            #exif = os.path.join(data.data_path, name) + '.exif'
            
            
        
        #exif_list = glob.glob(data.data_path) + 
        
        