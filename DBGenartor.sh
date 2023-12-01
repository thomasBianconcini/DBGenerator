#!/bin/bash

python3 dbGenerator.py
sudo docker build -t fakedb .

