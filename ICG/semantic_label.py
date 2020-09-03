import os
import cv2
import numpy as np
import argparse
from opensfm import dataset
from opensfm import features
from opensfm import pysfm
from collections import Counter

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
    for key in vote_dict:
        point = np.frombuffer(key)
        occurence_count = Counter(vote_dict[key])
        res = occurence_count.most_common(1)[0][0]
        color = None 
        if(res == 1):
            color = [255, 0, 0]
        else:
            color = [0, 255, 0]
        color = color.astype(np.uint8)
        row = np.hstack((point, color))
        pcl = np.vstack((pcl, row))
    
    return pcl

def label_pointcloud(data_path, semantics_path):
    #We take each shot, see which points fall on it and label it with corresponding semantic label.
    data = dataset.DataSet(data_path)
    reconstruction = data.load_reconstruction()[0]

    tracks_manager = data.load_tracks_manager()
    images = tracks_manager.get_shot_ids()
    
    imcount = 0
    ptcount = 0
    vote_dict = {}
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
        
        semantic_image_path = os.path.join(semantics_path, os.path.splitext(im)[0] + ".png")
        semantic_image = cv2.imread(semantic_image_path)
        print("Getting projections for image:  ", im)

        #TODO: Filter outliers by reprojection threshold? 
        #TODO: Create walkable area by filling up non object shit. 
        for i in range(len(pts3d)):
            pt2d = features.denormalized_image_coordinates(np.array(pts2d[i]).reshape(-1, 2), semantic_image.shape[1], semantic_image.shape[0])[0]
            # print(pt2d)
            row = int(pt2d[1])
            col = int(pt2d[0])
            # print(row, col)
            point = pts3d[i]
            
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
    
    print("Labeled ", ptcount, " points")
    print("Labeled for ", imcount, " images")
    pcl = get_pointcloud_from_vote(vote_dict)
    return pcl
        

if __name__=="__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument("data_path")
    parser.add_argument("semantics_path")
    args = parser.parse_args()
    labeled_pointcloud = label_pointcloud(args.data_path, args.semantics_path)
    np.savetxt("labeled_cloud.txt", labeled_pointcloud)

    