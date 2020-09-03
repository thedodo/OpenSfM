#Change between pointcloud formats. 
from pyntcloud import PyntCloud 
import argparse 

def main(src_fmt_path, dst_fmt_path):
    my_point_cloud = PyntCloud.from_file(src_fmt_path)
    my_point_cloud.to_file(dst_fmt_path)


if __name__=="__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument("src_fmt_path")
    parser.add_argument("dst_fmt_path")
    args = parser.parse_args()
    main(args.src_fmt_path, args.dst_fmt_path)

