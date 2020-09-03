import numpy as np
import json
import open3d as o3d
from opensfm import dataset
import os 

def flatten_coords_by_plane_proj(pt, points, plane, size):
    proj, dists = project_points_to_plane_xy(points, plane)
    pt_proj, pt_dists = project_points_to_plane_xy(pt, plane)

    #Normalize distances.
    proj_min = np.amin(proj, axis=0)
    proj_max = np.amax(proj, axis=0)
    proj_range = np.abs(proj_max - proj_min)

    #Get point closest to the lower bound.
    # orig_pt_idx = np.argmin(np.linalg.norm((proj - proj_min), axis = 1))
    orig_pt = proj_min #proj[orig_pt_idx, :]

    #Shift so that above pt is the origin.
    proj = proj - orig_pt  
    proj = proj / proj_range

    pt_proj = pt_proj - orig_pt
    pt_proj = pt_proj / proj_range

    #Scale coordinates to the aspect ratio we need.
    pt_proj = (np.floor(pt_proj * size)).astype(np.int32) 

    return pt_proj 

def get_camera2d(points, opensfm_data_path):
    opensfm_reconstruction_path = os.path.join(opensfm_data_path, "reconstruction.json")
    with open(opensfm_reconstruction_path) as f:
        data = json.load(f)[0]
    
    dset = dataset.DataSet(opensfm_data_path)
    reference = dset.load_reference()

    # print(data["shots"])
    shots = data["shots"]
    plane = np.array([0, 0, 1, 0])
    size = ((640, 480))
    
    pt3d = np.empty((0, 3))
    pt2d = np.empty((0, 2))
    gpsarr = np.empty((0, 3))
    for id in shots:
        shot = shots[id]
        point3d = np.asarray(shot['translation'])
        # print("point3d = ", point3d)
        point2d = flatten_coords_by_plane_proj(point3d, points, plane, size)
        gps = np.asarray(shot['gps_position'])

        pt3d = np.vstack((pt3d, point3d))
        pt2d = np.vstack((pt2d, point2d))
        gps = reference.to_lla(gps[0], gps[1], gps[2])
        gpsarr = np.vstack((gpsarr, gps))
    
    np.save("camera_points_3d.npy", pt3d)
    np.save("camera_points_2d.npy", pt2d)
    np.save("camera_points_gps.npy", gpsarr)

    print(gpsarr)

def project_points_to_plane_xy(points, plane, norm=False):
    dists_to_plane = points.dot(plane[:3][:, None]) + plane[3]
    pcd_proj = points - dists_to_plane * plane[:3][None, :]

    # pcd_proj_xy = pcd_proj[:, ::2] / pcd_proj[:, 1][:, None]
    # pcd_proj_xy = pcd_proj[:, ::2]

    plane_normal_dir = np.argmax(np.abs(plane[:3]))
    if plane_normal_dir == 0:
        pcd_proj_xy = pcd_proj[:, 1:]
        if norm:
            pcd_proj_xy /= pcd_proj[:, 0][:, None] + 1e-4
    elif plane_normal_dir == 1:
        pcd_proj_xy = pcd_proj[:, ::2]
        if norm:
            pcd_proj_xy /= pcd_proj[:, 1][:, None] + 1e-4
    elif plane_normal_dir == 2:
        pcd_proj_xy = pcd_proj[:, :2]
        if norm:
            pcd_proj_xy /= pcd_proj[:, 2][:, None] + 1e-4

    return pcd_proj_xy, dists_to_plane

    
def flatten_by_plane_proj(points, plane, size):
    proj, dists = project_points_to_plane_xy(points, plane)

    #Normalize distances.
    proj_min = np.amin(proj, axis=0)
    proj_max = np.amax(proj, axis=0)
    proj_range = np.abs(proj_max - proj_min)

    #Get point closest to the lower bound.
    #orig_pt_idx = np.argmin(np.linalg.norm((proj - proj_min), axis = 1))
    orig_pt = proj_min #proj[orig_pt_idx, :]

    #Shift so that above pt is the origin.
    proj = proj - orig_pt 
    proj = proj / proj_range

    #Scale coordinates to the aspect ratio we need.
    proj = (np.floor(proj * size)).astype(np.int32) 
    
    im = np.zeros((size[1] + 1, size[0] + 1))
    im[proj[:, 1], proj[:, 0]] = 255.0

    return im

if __name__== "__main__":
    pcloud_path = "/home/chetan/Documents/S4VI/sv4vi-icg/OpenSfM/data/lund/undistorted/depthmaps/merged.ply"
    opensfm_data_path = "/home/chetan/Documents/S4VI/sv4vi-icg/OpenSfM/data/lund/"
    
    pcloud = o3d.io.read_point_cloud(pcloud_path)
    points = np.asarray(pcloud.points)

    get_camera2d(points, opensfm_data_path)

