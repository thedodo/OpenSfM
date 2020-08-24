#Input: OpensFM data path. Plyfile path.

from opensfm import dataset
from opensfm import align
from opensfm import dense
import  argparse
from opensfm.align import align_reconstruction_naive_similarity, apply_similarity
from opensfm.dense import merge_depthmaps 
from pyntcloud import PyntCloud

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--opensfm_data_path", required=True)
    parser.add_argument("--plyfile_path", required=True)

    args = parser.parse_args()
    dset = dataset.DataSet(args.opensfm_data_path)
    udata = dataset.UndistortedDataSet(dset, "undistorted")
    reconstruction = udata.load_undistorted_reconstruction()[0]
    reference = dset.load_reference()
    cloud = PyntCloud.from_file(args.plyfile_path)
    xyz = cloud.xyz

    for i in range(xyz.shape[0]):
        xyz[i, :] = reference.to_lla(xyz[i, 0], xyz[i, 1], xyz[i, 2])

    cloud.xyz = xyz 
    cloud.to_file("merged_geo.ply")
    print(cloud.xyz)
    print("Saved pointcloud with Lat Long Alt coordinates")
    #Replace shot gps positions with exif data. 
    # reference = dset.load_reference()

    # s, A, b = align_reconstruction_naive_similarity(dset.config, reconstruction, None)
    # print("\ns: ", s,"\n\nA: ", A, "\n\nb:",b)
    # apply_similarity(reconstruction, s, A, b)

    
    # merge_depthmaps(udata, reconstruction)
