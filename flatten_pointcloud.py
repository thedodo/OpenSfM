import numpy as np


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
    im = np.zeros([y_max, x_max], dtype=np.uint8)

    # FILL PIXEL VALUES IN IMAGE ARRAY
    im[y_img, x_img] = pixel_values
   
    return im

def flatten_by_plane_proj(points, plane, size):
    print("Shape of point - entering shit!", points.shape)
    proj, dists = project_points_to_plane_xy(points, plane)
    print("Shape of point - entering shit!", points.shape)

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
    
    # if(points.shape[1] == 3):
    #     im = np.zeros((size[1] + 1, size[0] + 1))
    #     im[proj[:, 1], proj[:, 0]] = 255.0
    #     return im
    
    # elif(points.shape[1] == 6):
    im = np.ones((size[1] + 1, size[0] + 1, 3), np.uint8) * 255;
    print("For flattening colors: ")
    for i in range(proj.shape[0]):
        im[proj[i, 1], proj[i, 0], :] = points[i, 3:]
        print(im[proj[i, 1], proj[i, 0], :])
    return im
    
    # return None


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

def flatten_coordinates(points, res=0.1, side_range=(-10., 10.), fwd_range = (-10., 10.), height_range=(-2., 2.)):
    # EXTRACT THE POINTS FOR EACH AXIS
    x_points = points[:, 0]
    y_points = points[:, 1]
    z_points = points[:, 2]

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
    
    pts = np.hstack((x_img[:, np.newaxis], y_img[:, np.newaxis]))
    return pts