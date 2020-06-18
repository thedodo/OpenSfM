#Input: OpensFM data path. Plyfile path.
import sys
sys.path.append("../ICG")

from opensfm import dataset
import  argparse
from align import align_reconstruction_naive_similarity, apply_similarity
from dense import merge_depthmaps 

if __name__ == "main":
    parser = argaparse.ArgumentParser()
    parser.add_argument("--opensfm_data_path", required=True)
    parser.add_argument("--plyfile_path", required=True)

    args = parser.parse_args()

    dset = dataset.DataSet(args.opensfm_data_path)
    reconstruction = dset.load_reconstruction()

    s, A, b = align_reconstruction_naive_similarity(dset.config, reconstruction, None)
    apply_similarity(reconstruction, s, A, b)

    udata = dset.UndistortedDataSet(dset, None)
    recon_udata = udata.load_undistorted_reconstruction() 

    merge_depthmaps(udata, recon_udata)
