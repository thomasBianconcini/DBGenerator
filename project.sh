#!/bin/bash
port=8080
while getopts p: flag
do
    case "${flag}" in
        p) port=${OPTARG};;
    esac
done

echo $port

sudo docker run -p $port:5000 -e HOST="0.0.0.0" -v /home/thomas/Desktop/progettoCyber:/app fakedb


