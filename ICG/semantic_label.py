import os
import cv2
import numpy as np
import argparse
from opensfm import dataset
from opensfm import features
from opensfm import pysfm
from collections import Counter
from flatten_pointcloud import flatten_by_plane_proj, flatten_coords_by_plane_proj

def get_shot_observations(tracks_manager, reconstruction, camera, shot):
    bs, Xs, ids = [], [], []
    for track, obs in tracks_manager.get_shot_observations(shot).items():
        if track in reconstruction.points:
            b = obs.point
            bs.append(b)
            Xs.append(reconstruction.points[track].coordinates)
            ids.append(track)
    
    return bs, Xs

def get_pointcloud_from_vote(vote_dict):
    pcl = np.empty((0, 6))
    groundPoints = np.empty((0, 3))
    for key in vote_dict:
        point = np.frombuffer(key)
        occurence_count = Counter(vote_dict[key])
        res = occurence_count.most_common(1)[0][0]
        color = None 
        if(res == 1):
            groundPoints = np.vstack((groundPoints, point))
            continue
        else:
            color = np.array([0, 255, 0])
        color = color.astype(np.uint8)
        row = np.hstack((point, color))
        pcl = np.vstack((pcl, row))
    
    return pcl, groundPoints

def testInlier(point3, point2, camera, shot, threshold): #TODO: Fix this, this has probelms!
    b = camera.pixel_bearing(point2)
    R = shot.pose.get_rotation_matrix()
    t = shot.pose.translation

    reprojected_b = R.T.dot((point3 - t).T).T
    reprojected_b /= np.linalg.norm(reprojected_b)

    # print(reprojected_b, " ", b)

    reproj_error = np.linalg.norm(reprojected_b - b)

    return (reproj_error < threshold)

# def getGroundPlane(pcl):
#     #TODO: get ground plane by taking a bunch of points that are closest to z 

def samplePlanePoints(plane, boundMin, boundMax):
    ptlist = []
    if(plane is None):
        ##Return z=0 plane by default. 
        for x in range(int(boundMin[1]), int(boundMax[1])):
            for y in range(int(boundMin[0]), int(boundMax[1])):
                pt = np.array([x, y, 0])
                ptlist.append(pt)
        
        return ptlist

    return ptlist 


def getPointColorFromReconstruction(reconstruction, image_dir, point):
    label_list = []
    for shot_id in reconstruction.shots:
        shot = reconstruction.shots[shot_id]
        norm_projection = shot.project(point)
        image_path = os.path.join(image_dir, os.path.splitext(shot.id)[0] + ".png")
        # print("Projecting onto ", image_path)
        image = cv2.imread(image_path)
        pt_im = features.denormalized_image_coordinates(np.array(norm_projection).reshape(-1, 2), image.shape[1], image.shape[0])[0]
        # print(pt_im)
        row = int(pt_im[1])
        col = int(pt_im[0])
        if((row in range(0, image.shape[0]) and (col in range(0, image.shape[0])))):
            rgb = image[row, col]
            # print(rgb)
            if(np.all(rgb == np.array([98, 98, 98]))):
                rgb = 1
            elif(np.all(rgb == np.array([100, 100, 100]))):
                rgb = 1
            else:
                rgb = 2
            label_list.append(rgb)
    
    if (len(label_list)==0):
        return None 
    occurence_count = Counter(label_list)
    res = occurence_count.most_common(1)[0][0]
    if(res == 1):
        res = [0, 255, 255]
    else:
        res = [0, 0, 255]
    return res 

def label_pointcloud(data_path, semantics_path):
    #We take each shot, see which points fall on it and label it with corresponding semantic label.
    data = dataset.DataSet(data_path)
    reconstruction = data.load_reconstruction()[0]

    tracks_manager = data.load_tracks_manager()
    images = tracks_manager.get_shot_ids()
    
    imcount = 0
    ptcount = 0
    vote_dict = {}
    campose = np.empty((0, 3))
    for im in images:
        if(not(data.load_exif(im)['camera'] in reconstruction.cameras)):
            continue
        camera = reconstruction.cameras[data.load_exif(im)['camera']]
        # print("Camera W, H ", camera.width, camera.height)
        pts2d, pts3d = get_shot_observations(tracks_manager, reconstruction, camera, im)
        if(not (im in reconstruction.shots)):
            print(im, " not in shots!")
            continue
        shot = reconstruction.shots[im]
        
        campose = np.vstack((campose, shot.pose.translation))
        semantic_image_path = os.path.join(semantics_path, os.path.splitext(im)[0] + ".png")
        semantic_image = cv2.imread(semantic_image_path)
        print("Getting projections for image:  ", im)

        #TODO: Filter outliers by reprojection threshold? 
        #TODO: Create walkable area by filling up non object shit.
        pointcloud = np.empty((0, 3))
        for i in range(len(pts3d)):
            # inlier = testInlier(pts3d[i], pts2d[i], camera, shot, 0.004) #resection_threshold from config.py
            # if(not(inlier)):
            #     continue 
            pt2d = features.denormalized_image_coordinates(np.array(pts2d[i]).reshape(-1, 2), semantic_image.shape[1], semantic_image.shape[0])[0]
            # print(pt2d)
            row = int(pt2d[1])
            col = int(pt2d[0])
            # print(row, col)
            point = pts3d[i]
            pointcloud = np.vstack((pointcloud, point))
            
            if(not(point.tobytes() in vote_dict)):
                vote_dict[point.tobytes()] = []
            
            rgb = semantic_image[row, col]
            if(np.all(rgb == np.array([98, 98, 98]))):
                rgb = 1
            elif(np.all(rgb == np.array([100, 100, 100]))):
                rgb = 1
            else:
                rgb = 2
            
            vote_dict[point.tobytes()].append(rgb)
            ptcount = ptcount + 1
        
        imcount = imcount + 1
    
    pcl, groundPoints = get_pointcloud_from_vote(vote_dict)
    print(groundPoints)

    #Fill up the non-walkable area.
    planePointSet = pcl[:12000, :3]
    # if(groundPoints.shape[0] > 2):
    #     planePointSet = groundPoints
    boundMin = np.amin(planePointSet, axis=0)
    boundMax = np.amax(planePointSet, axis=0)
    planePtList = samplePlanePoints(None, boundMin, boundMax)
    validPlanePts = np.empty((0, 6))
    count = 0
    n_elem = 1000
    interval = int(len(planePtList) / n_elem)
    planePtList = planePtList[::interval]
    for planePt in planePtList:
        color = getPointColorFromReconstruction(reconstruction, semantics_path, planePt)
        if(color is None):
            continue
        validPt = np.hstack((planePt, color))
        validPlanePts = np.vstack((validPlanePts, validPt))
        labelCompletionPercent = int(count/len(planePtList) * 100)
        if(count % 20 == 0):
            print("Completed ", labelCompletionPercent, "% of labeling")
        count = count + 1
    
    final_pcl = np.vstack((pcl[:12000, :], validPlanePts))
    print("We got ", validPlanePts.shape[0], " valid plane points")
    # final_pcl = pcl[:12000, :]
    print("Labeled ", ptcount, " points")
    print("Labeled for ", imcount, " images")
    flat = flatten_by_plane_proj(final_pcl[:, :3], np.array([0, 0, 1, 0]), (640, 480), final_pcl[:, 3:])
    # for pt in campose:
    #     ptproj = flatten_coords_by_plane_proj(pt, final_pcl[:, :3], np.array([0, 0, 1, 0]), (640, 480))
    #     flat[ptproj[0, 1], ptproj[0, 0], :] = np.array([0, 0, 255])

    cv2.imwrite("flattened_img.jpg", flat)
    return pcl
        

if __name__=="__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument("data_path")
    parser.add_argument("semantics_path")
    args = parser.parse_args()
    labeled_pointcloud = label_pointcloud(args.data_path, args.semantics_path)
    np.savetxt("labeled_cloud.txt", labeled_pointcloud)