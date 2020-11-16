import numpy as np
import cv2
from plyfile import PlyData
import json
import open3d as o3d
from opensfm import dataset
from opensfm import features
from opensfm import pysfm
from collections import Counter
import os 
import sys
import argparse



#def cleanPLY(ply_path, ply_cleaned):



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--opensfm_data_path", required=True)
    parser.add_argument("--high",type=float)
    parser.add_argument("--low", type=float)
    args = parser.parse_args()


    ply_path = args.opensfm_data_path + '/undistorted/depthmaps/merged.ply'
    ply_cleaned = args.opensfm_data_path + '/undistorted/depthmaps/merged_clean.ply'
    
    plydata = PlyData.read(ply_path)
        
    x_arr = np.array(plydata.elements[0].data['x'])
    y_arr = np.array(plydata.elements[0].data['y'])
    z_arr = np.array(plydata.elements[0].data['z'])
    
    
    r_arr = np.array(plydata.elements[0].data['diffuse_red'])
    g_arr = np.array(plydata.elements[0].data['diffuse_green'])
    b_arr = np.array(plydata.elements[0].data['diffuse_blue'])
    
    #high = np.percentile(z_arr,99.5)
    #low = np.percentile(z_arr, 2)     
    
    high = np.percentile(z_arr,args.high)
    low = np.percentile(z_arr, args.low)     
    
    
    idx_bad_pos = np.where(z_arr > high)
    idx_bad_neg = np.where(z_arr < low)
    
    idx_bad = np.concatenate((idx_bad_pos, idx_bad_neg), axis=1)[0]
    
    x_arr_new = np.delete(x_arr, idx_bad)
    y_arr_new = np.delete(y_arr, idx_bad)
    z_arr_new = np.delete(z_arr, idx_bad)
    
    r_arr_new = np.delete(r_arr, idx_bad)
    g_arr_new = np.delete(g_arr, idx_bad)
    b_arr_new = np.delete(b_arr, idx_bad)
    
    
    points = []    
    for pt_count in range(0, len(x_arr_new)):
        
        points.append("%f %f %f %d %d %d 0\n"%(x_arr_new[pt_count] ,y_arr_new[pt_count] ,z_arr_new[pt_count] ,r_arr_new[pt_count] ,g_arr_new[pt_count], b_arr_new[pt_count]))
    
    
    file = open(ply_cleaned,"w")
    file.write('''ply
    #format ascii 1.0
    #element vertex %d
    #property float x
    #property float y
    #property float z
    #property uchar red
    #property uchar green
    #property uchar blue
    #property uchar alpha
    #end_header
    #%s
    #'''%(len(x_arr_new),"".join(points)))
    
    file.close()
