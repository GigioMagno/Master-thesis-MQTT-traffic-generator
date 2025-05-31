#!/bin/bash

# 1. Crea rete Docker personalizzata
docker network create --driver=bridge --subnet=192.168.100.0/24 small_smarthome_network

# 2. Dockerfile per immagine con MQTT + Python + Pandas + Scapy + paho
cat <<EOF > Dockerfile.mqtt
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Installa pacchetti
RUN apt-get update && \\
    apt-get install -y mosquitto mosquitto-clients python3 python3-pip paho iproute2 iputils-ping net-tools && \\
    pip3 install pandas scapy && \\
    apt-get clean

# Crea directory di configurazione Mosquitto
RUN mkdir -p /etc/mosquitto/

# Configurazione base per accettare connessioni da tutti
RUN echo "listener 1883" > /etc/mosquitto/mosquitto.conf && \\
    echo "allow_anonymous true" >> /etc/mosquitto/mosquitto.conf

# Avvia Mosquitto solo nel container broker
CMD if [ "\$HOSTNAME" = "broker" ]; then \\
        mosquitto -c /etc/mosquitto/mosquitto.conf; \\
    else \\
        /bin/bash; \\
    fi
EOF

# 3. Build immagine personalizzata
docker build -t mqtt_lab -f Dockerfile.mqtt .

# 4. Avvia i container
docker run -dit \
  --name broker \
  --network=small_smarthome_network \
  --cap-add=NET_ADMIN \
  --memory="64m" \
  --cpus="1.0" \
  mqtt_lab

docker run -dit \
  --name publisher \
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
docker inspect -f '{{.Name}} - {{.NetworkSettings.Networks.small_smarthome_network.IPAddress}}' broker
docker inspect -f '{{.Name}} - {{.NetworkSettings.Networks.small_smarthome_network.IPAddress}}' publisher
docker inspect -f '{{.Name}} - {{.NetworkSettings.Networks.small_smarthome_network.IPAddress}}' subscriber