#!/bin/bash

docker exec -it publisher bash
tc qdisc del dev eth0 root

docker exec -it broker bash
tc qdisc del dev eth0 root

docker exec -it subscriber bash
tc qdisc del dev eth0 root