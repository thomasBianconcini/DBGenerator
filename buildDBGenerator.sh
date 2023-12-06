#!/bin/bash

pip install faker
sudo apt-get -y install sqlite3

file_to_delete="fakeDB.db"

if [ -f "$file_to_delete" ] ; then
    rm "$file_to_delete"
fi


python3 dbGenerator.py
sudo docker build -t fakedb .