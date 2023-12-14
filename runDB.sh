#!/bin/bash
port=8080

while getopts p: flag
do
    case "${flag}" in
        p) port=${OPTARG};;
    esac
done

echo "Porta da cui si può accedere al DB è: "$port
echo "Ti verrà richiesta la password da utilizzare per accedere al DB..."
sudo docker run -it -p $port:5000 -e HOST="0.0.0.0" fakedb
