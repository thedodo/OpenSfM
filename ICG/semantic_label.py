import os
from __future__ import print_function
import numpy as np
import argparse
from opensfm import dataset
from opensfm import features

if __name__=="__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument("data_path")
    parser.add_argument("semantics_path")
    args = parser.parse_args()

    