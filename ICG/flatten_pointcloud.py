import numpy as np
import cv2
from plyfile import PlyData
import json
import open3d as o3d
from opensfm import dataset
import os 
import sys

# ==============================================================================
#                                                                   SCALE_TO_255
# ==============================================================================
def scale_to_255(a, min, max, dtype=np.uint8):
    """ Scales an array of values from specified min, max range to 0-255
        Optionally specify the data type of the output (default is uint8)
    """
    return (((a - min) / float(max - min)) * 255).astype(dtype)


# ==============================================================================
#                                                         POINT_CLOUD_2_BIRDSEYE
# ==============================================================================
def flatten_pcl(points, res=0.1, side_range=(-10., 10.), fwd_range = (-10., 10.), height_range=(-2., 2.)):
    """ Creates an 2D birds eye view representation of the point cloud data.
    Args:
        points:     (numpy array)
                    N rows of points data
                    Each point should be specified by at least 3 elements x,y,z
        res:        (float)
                    Desired resolution in metres to use. Each output pixel will
                    represent an square region res x res in size.
        side_range: (tuple of two floats)
                    (-left, right) in metres
                    left and right limits of rectangle to look at.
        fwd_range:  (tuple of two floats)
                    (-behind, front) in metres
                    back and front limits of rectangle to look at.
        height_range: (tuple of two floats)
                    (min, max) heights (in metres) relative to the origin.
                    All height values will be clipped to this min and max value,
                    such that anything below min will be truncated to min, and
                    the same for values above max.
    Returns:
        2D numpy array representing an image of the birds eye view.
    """
    # EXTRACT THE POINTS FOR EACH AXIS
    x_points = points[:, 0]
    y_points = points[:, 1]
    z_points = points[:, 2]
    #z_points = np.ones(z_points.shape) * 255

    # FILTER - To return only indices of points within desired cube
    # Three filters for: Front-to-back, side-to-side, and height ranges
    # Note left side is positive y axis in LIDAR coordinates
    f_filt = np.logical_and((x_points > fwd_range[0]), (x_points < fwd_range[1]))
    s_filt = np.logical_and((y_points > -side_range[1]), (y_points < -side_range[0]))
    filter = np.logical_and(f_filt, s_filt)
    indices = np.argwhere(filter).flatten()

    # KEEPERS
    x_points = x_points[indices]
    y_points = y_points[indices]
    z_points = z_points[indices]

    # CONVERT TO PIXEL POSITION VALUES - Based on resolution
    x_img = (-y_points / res).astype(np.int32)  # x axis is -y in LIDAR
    y_img = (-x_points / res).astype(np.int32)  # y axis is -x in LIDAR

    # SHIFT PIXELS TO HAVE MINIMUM BE (0,0)
    # floor & ceil used to prevent anything being rounded to below 0 after shift
    
    x_img -= int(np.floor(side_range[0] / res))
    y_img += int(np.ceil(fwd_range[1] / res))

    # CLIP HEIGHT VALUES - to between min and max heights
    pixel_values = np.clip(a=z_points,
                           a_min=height_range[0],
                           a_max=height_range[1])

    # RESCALE THE HEIGHT VALUES - to be between the range 0-255
    pixel_values = scale_to_255(pixel_values,
                                min=height_range[0],
                                max=height_range[1])

    # INITIALIZE EMPTY ARRAY - of the dimensions we want
    x_max = 1 + int((side_range[1] - side_range[0]) / res)
    y_max = 1 + int((fwd_range[1] - fwd_range[0]) / res)
    im = np.zeros([y_max + 1, x_max + 1], dtype=np.uint8)

    # FILL PIXEL VALUES IN IMAGE ARRAY
    im[y_img, x_img] = pixel_values
   
    return im


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

 
    
def cleanPLY(ply_path, ply_cleaned):

    plydata = PlyData.read(ply_path)
        
    x_arr = np.array(plydata.elements[0].data['x'])
    y_arr = np.array(plydata.elements[0].data['y'])
    z_arr = np.array(plydata.elements[0].data['z'])
    
    
    r_arr = np.array(plydata.elements[0].data['diffuse_red'])
    g_arr = np.array(plydata.elements[0].data['diffuse_green'])
    b_arr = np.array(plydata.elements[0].data['diffuse_blue'])
    
    high = np.percentile(z_arr,99.5)
    low = np.percentile(z_arr, 2)     
    
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


def flatten_by_plane_proj(points, plane, size, colors):
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
    
    im = np.zeros((size[1] + 1, size[0] + 1,3))
    im[proj[:, 1], proj[:, 0],:] = colors * 255

    return im

def flatten_coords_by_plane_proj(pt, points, plane, size):
    
    #points = np.vstack((points, pt))

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

def get_camera2d(points, opensfm_data_path, size):
    
    opensfm_reconstruction_path = opensfm_data_path + "/reconstruction.json"
    with open(opensfm_reconstruction_path) as f:
        data = json.load(f)[0]
    
    dset = dataset.DataSet(opensfm_data_path)
    reference = dset.load_reference()

    # print(data["shots"])
    shots = data["shots"]
    plane = np.array([0, 0, 1, 0])
    
    pt3d = np.empty((0, 3))
    pt2d = np.empty((0, 2))
    gpsarr = np.empty((0, 3))
    for id in shots:
        shot = shots[id]
        point3d = np.asarray(shot['translation'])
        # print("point3d = ", point3d)
        gps = np.asarray(shot['gps_position'])
        
        point2d = flatten_coords_by_plane_proj(pt3d, points, plane, size)

        pt3d = np.vstack((pt3d, point3d))
        pt2d = np.vstack((pt2d, point2d))
        gps = reference.to_lla(gps[0], gps[1], gps[2])
        gpsarr = np.vstack((gpsarr, gps))
        
    return pt3d, pt2d, gpsarr


def getNormPos(campos, size):
    
    campos_norm = np.zeros((len(campos[:,0]),2))
    
    x_m = size[0]/2
    y_m = size[1]/2
    
    campos_norm[:,0] = (campos[:,0] - x_m) * 0.1
    campos_norm[:,1] = (campos[:,1] - y_m) * 0.1
    
    
    return campos_norm



reconstruction_path = sys.argv[1]

os.system('mkdir ' + reconstruction_path + '/flatten')
pcloud_path = reconstruction_path + '/undistorted/depthmaps/merged.ply'

#To read pointcloud
#pcloud = o3d.io.read_point_cloud(pcloud_path)
#points = np.asarray(pcloud.points)


plydata = PlyData.read(pcloud_path)
    
x_arr = np.array(plydata.elements[0].data['x'])
y_arr = np.array(plydata.elements[0].data['y'])
z_arr = np.array(plydata.elements[0].data['z'])


r_arr = np.array(plydata.elements[0].data['diffuse_red'])
g_arr = np.array(plydata.elements[0].data['diffuse_green'])
b_arr = np.array(plydata.elements[0].data['diffuse_blue'])

xyz = np.dstack((x_arr,y_arr,z_arr))
colors = np.dstack((b_arr, g_arr, r_arr))

xyz = np.squeeze(xyz)
colors = np.squeeze(colors)

bounds_min = np.amin(xyz, axis = 0)
bounds_max = np.amax(xyz, axis=0)
side_range = (bounds_min[1]-50, bounds_max[1] + 20)
fwd_range = (bounds_min[0] , bounds_max[0])
height_range = (bounds_min[2], bounds_max[2])

flat_im2 = flatten_pcl(xyz, 0.1, side_range, fwd_range, height_range)

#print(flat_im2.shape)


pt3d, pt2d, gpsarr = get_camera2d(xyz, reconstruction_path, (flat_im2.shape[0],flat_im2.shape[1]))
pt2d = pt2d.astype(np.uint8)

#gray to color so markers can be red!
flat_im2 = np.dstack((flat_im2,flat_im2,flat_im2))

#print(flat_im2.shape)

for i in range (0,len(pt2d)):
    
    y_pos = pt2d[i,0]
    x_pos = pt2d[i,1]
    #print('pos: {},{}'.format(y_pos,x_pos))
    
    flat_im2[(y_pos-3):(y_pos+3),(x_pos-3):(x_pos+3),:] = np.array([0,0,255])


cv2.imwrite(reconstruction_path + '/flatten/flatten_ply2.jpeg', flat_im2)

#size should be dynamic!
flat_im = flatten_by_plane_proj(xyz, np.array([0,0,1,0]), (flat_im2.shape[0],flat_im2.shape[1]), colors)

cv2.imwrite(reconstruction_path + '/flatten/flatten_ply.jpeg', flat_im)
