# parser_runner.py

import sys
from scapy.all import PcapReader, TCP
from scapy.contrib.mqtt import MQTT
from Utils.MQTTP import MQTTv3Parser

def run_scapy(pcap_file):
    packets = PcapReader(pcap_file)
    for pkt in packets:
        try:
            _ = pkt[MQTT]
        except Exception:
            pass

def run_MQTTP(pcap_file):
    packets = PcapReader(pcap_file)
    for pkt in packets:
        try:
            raw = bytes(pkt[TCP].payload)
            msg_type = raw[0] & 0xF0
            if msg_type == 0x10:
                MQTTv3Parser.ParseConnectPacket(raw)
            elif msg_type == 0x30:
                MQTTv3Parser.ParsePublishPacket(raw)
            elif msg_type == 0x80:
                MQTTv3Parser.ParseSubscribePacket(raw)
        except Exception:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parser_runner.py <pcap_file> <Scapy|MQTTP>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    mode = sys.argv[2]

    if mode == "Scapy":
        run_scapy(pcap_file)
    elif mode == "MQTTP":
        run_MQTTP(pcap_file)
    else:
        print("Invalid mode. Choose 'Scapy' or 'MQTTP'.")
