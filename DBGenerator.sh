#!/bin/bash

pip install -r requirements.txt


file_to_delete="fakeDB.db"

if [ -f "$file_to_delete" ] ; then
    rm "$file_to_delete"
fi


python3 dbGenerator.py
sudo docker build -t fakedb .

