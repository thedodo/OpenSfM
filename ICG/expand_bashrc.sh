#!/bin/bash

echo "export PYTHONPATH="\$\{PYTHONPATH\}":${PWD}" >> ~/.bashrc
source ~/.bashrc
