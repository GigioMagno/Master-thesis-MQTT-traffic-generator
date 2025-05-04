from scapy.all import rdpcap
from scapy.contrib.mqtt import MQTT, MQTTConnect

pcap_path = "generated_traffic_2025-05-04_11-03-08.pcap"
packets = rdpcap(pcap_path)

mqtt_connects = []

for pkt in packets:
    if MQTT in pkt and MQTTConnect in pkt[MQTT]:
        try:
            client_id = pkt[MQTT][MQTTConnect].clientId.decode("utf-8", errors="ignore")
            mqtt_connects.append(client_id)
        except Exception:
            mqtt_connects.append("Errore lettura clientId")

print("ClientId trovati nei pacchetti MQTTConnect:")
print(mqtt_connects)
