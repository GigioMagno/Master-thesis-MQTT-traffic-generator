#!/bin/bash

# 1. Crea rete Docker personalizzata
docker network create --driver=bridge --subnet=192.168.100.0/24 small_smarthome_network

# 2. Dockerfile per immagine con MQTT + Python + Pandas + Scapy
cat <<EOF > Dockerfile.mqtt
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y mosquitto python3 python3-pip iproute2 iputils-ping net-tools && \
    pip3 install pandas scapy && \
    apt-get clean

CMD ["/bin/bash"]
EOF

# 3. Build immagine personalizzata
docker build -t mqtt_lab -f Dockerfile.mqtt .

# 4. Avvia tre container sulla rete "small_smarthome_network" con limiti di risorse
docker run -dit \
  --name publisher \
  --network=small_smarthome_network \
  --cap-add=NET_ADMIN \
  --memory="64m" \
  --cpus="1.0" \
  mqtt_lab

docker run -dit \
  --name broker \
  --network=small_smarthome_network \
  --cap-add=NET_ADMIN \
  --memory="64m" \
  --cpus="1.0" \
  mqtt_lab

docker run -dit \
  --name subscriber \
  --network=small_smarthome_network \
  --cap-add=NET_ADMIN \
  --memory="64m" \
  --cpus="1.0" \
  mqtt_lab

# 5. Mostra IP dei container
echo "[INFO] IP dei container:"
docker inspect -f '{{.Name}} - {{.NetworkSettings.Networks.small_smarthome_network.IPAddress}}' publisher
docker inspect -f '{{.Name}} - {{.NetworkSettings.Networks.small_smarthome_network.IPAddress}}' broker
docker inspect -f '{{.Name}} - {{.NetworkSettings.Networks.small_smarthome_network.IPAddress}}' subscriber

echo "[INFO] Ambiente pronto. Esegui:"
echo "    docker exec -it publisher bash"
echo "    docker exec -it broker bash"
echo "    docker exec -it subscriber bash"
