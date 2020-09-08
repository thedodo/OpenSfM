#!/bin/bash
sudo apt-get install -y \
        build-essential \
        cmake \
        git \
        libatlas-base-dev \
        libeigen3-dev \
        libgoogle-glog-dev \
        libopencv-dev \
        libsuitesparse-dev \
        python3-dev \
        python3-numpy \
        python3-opencv \
        python3-pip \
        python3-pyproj \
        python3-scipy \
        python3-yaml \
        curl \ vim \
    
pip3 install exifread==2.1.2 \
                gpxpy==1.1.2 \
                networkx==1.11 \
                numpy \
                pyproj==1.9.5.1 \
                pytest==3.0.7 \
                python-dateutil==2.6.0 \
                PyYAML==3.12 \
                scipy \
                xmltodict==0.10.2 \
                cloudpickle==0.4.0 \
                loky

             
cd ..
mkdir source 
cd source
sudo wget http://ceres-solver.org/ceres-solver-1.14.0.tar.gz
tar -xf ceres-solver-1.14.0.tar.gz
cd ceres-solver-1.14.0
sudo mkdir -p build
cd build
sudo cmake .. -DCMAKE_C_FLAGS=-fPIC -DCMAKE_CXX_FLAGS=-fPIC -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF
sudo make -j8 install
cd ../..
sudo rm -R ceres-solver-1.14.0
git clone https://github.com/paulinus/opengv.git
cd opengv/
#git submodule update --init --recursive
sudo mkdir build
cd build
sudo cmake .. -DBUILD_PYTHON=ON -DPYBIND11_PYTHON_VERSION=3.6 -DPYTHON_INSTALL_DIR=/usr/local/lib/python3.6/dist-packages/
sudo make -j8 install
cd ../../..
sudo python setup.py build
pip3 install repoze.lru
pip3 install open3d
pip3 install plyfile
sudo apt-get install build-essential
sudo apt-get install python-all-dev
sudo apt-get install libexiv2-dev
sudo apt-get install libboost-python-dev
pip3 install piexif
