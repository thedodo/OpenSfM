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
        python-dev \
        python-numpy \
        python-opencv \
        python-pip \
        python-pyexiv2 \
        python-pyproj \
        python-scipy \
        python-yaml \
        curl \
    
pip install exifread==2.1.2 \
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
                loky==1.2.1

git clone --recursive https://github.com/mapillary/OpenSfM  
             
cd OpenSfM
sudo apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        libatlas-base-dev \
        libeigen3-dev \
        libgoogle-glog-dev \
        libopencv-dev \
        libsuitesparse-dev \
        python-dev \
        python-numpy \
        python-opencv \
        python-pip \
        python-pyexiv2 \
        python-pyproj \
        python-scipy \
        python-yaml \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
mkdir source 
cd source
wget http://ceres-solver.org/ceres-solver-1.14.0.tar.gz
tar -xf ceres-solver-1.14.0.tar.gz
cd ceres-solver-1.14.0
mkdir -p build
cd build
cmake .. -DCMAKE_C_FLAGS=-fPIC -DCMAKE_CXX_FLAGS=-fPIC -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF
sudo make -j4 install
cd ../..
sudo rm -R ceres-solver-1.14.0
git clone https://github.com/paulinus/opengv.git
cd opengv/
git submodule update --init --recursive
mkdir -p build
cd build
cmake .. -DBUILD_PYTHON=ON -DPYBIND11_PYTHON_VERSION=3.6 -DPYTHON_INSTALL_DIR=/usr/local/lib/python3.6/dist-packages/
sudo make install
cd ../../..
python setup.py build
pip install repoze.lru