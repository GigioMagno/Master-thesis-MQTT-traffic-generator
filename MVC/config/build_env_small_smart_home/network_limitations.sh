#!/bin/bash

# Sul container publisher
docker exec -it publisher bash
tc qdisc add dev eth0 root netem delay 80ms loss 10%

# Sul container broker
docker exec -it broker bash
tc qdisc add dev eth0 root netem delay 200ms loss 10%

# Sul container subscriber
docker exec -it subscriber bash
tc qdisc add dev eth0 root netem delay 100ms loss10%
