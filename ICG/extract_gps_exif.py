import numpy as np
import os 
import sys
import glob
import json




if len (sys.argv) != 2 :
    print("Usage: python add_gps2jpg.py folder")
    sys.exit (1)


folder = sys.argv[1]
exif_list = glob.glob(folder + '/exif/*.exif')


file_out = open(folder + 'gps_coord.txt', 'w+')
file_out.write('latitude,longitude\n')
for i in range(len(exif_list)):
    
    
    
    f = open(exif_list[i],) 
      
    # returns JSON object as  
    # a dictionary 
    data = json.load(f) 
    f.close() 
      
    # Iterating through the json 
    # list 
    lat = data['gps']['latitude']
    long = data['gps']['longitude']
    # Closing file 
    gps_tag = str(lat) + ',' + str(long) + '\n'
    file_out.write(gps_tag)
    
file_out.close()