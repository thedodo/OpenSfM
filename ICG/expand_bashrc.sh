#!/bin/bash

echo "export PYTHONPATH="\$\{PYTHONPATH\}":${PWD}" >> ~/.bashrc
echo "export PYTHONPATH="\$\{PYTHONPATH\}":${PWD}/ICG" >> ~/.bashrc

source ~/.bashrc
