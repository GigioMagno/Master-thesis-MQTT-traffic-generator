#!/bin/bash

docker rm -f publisher broker subscriber
docker network rm small_smarthome_network
#Uncomment do avoid image caching
#docker image rm mqtt_lab
#rm Dockerfile.mqtt
