from scapy.all import rdpcap, TCP
from scapy.contrib.mqtt import MQTT
from Utils.MQTTP import MQTTv3Parser
from memory_profiler import memory_usage
import matplotlib.pyplot as plt
import time
import sys

def extract_mqtt3_packets(pcap_path):
    packets = rdpcap(pcap_path)
    mqtt3_packets = []

    for pkt in packets:
        if TCP in pkt and pkt.haslayer(MQTT):
            try:
                proto_level = int(bytes(pkt[MQTT])[7])
                if proto_level == 4:  # MQTT 3.1.1
                    mqtt3_packets.append(pkt)
            except Exception:
                continue
    return mqtt3_packets

def run_scapy_parser(packets):
    for pkt in packets:
        try:
            _ = pkt[MQTT]  # Scapy parser
        except Exception:
            pass

def run_custom_parser(packets):
    for pkt in packets:
        try:
            raw = bytes(pkt[TCP].payload)
            msg_type = raw[0] & 0xF0

            if msg_type == 0x10:  # CONNECT
                MQTTv3Parser.ParseConnectPacket(raw)
            elif msg_type == 0x30:  # PUBLISH
                MQTTv3Parser.ParsePublishPacket(raw)
            elif msg_type == 0x80:  # SUBSCRIBE
                MQTTv3Parser.ParseSubscribePacket(raw)
            else:
                continue  # altri tipi ignorati
        except Exception:
            pass

def benchmark(name, func, packets):
    print(f"{name}")
    start = time.time()
    mem = memory_usage((func, (packets,)), interval=0.05)
    end = time.time()
    duration = end - start
    peak = max(mem) - min(mem)
    return duration, peak, mem

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compare_scapy_vs_mylib_mqtt3.py <file.pcap>")
        sys.exit(1)

    pcap_file = sys.argv[1]
    print(f"\nCaricamento pacchetti MQTT v3 da {pcap_file}...")

    all_packets = extract_mqtt3_packets(pcap_file)
    print(f"Trovati {len(all_packets)} pacchetti MQTT v3")

    if len(all_packets) == 0:
        print("Nessun pacchetto MQTT v3 trovato.")
        sys.exit(0)

    results = {}
    dur, mem, trace1 = benchmark("Parsing con Scapy", run_scapy_parser, all_packets)
    results["Scapy"] = (dur, mem, trace1)

    dur, mem, trace2 = benchmark("Parsing con la MQTTP", run_custom_parser, all_packets)
    results["MQTTP"] = (dur, mem, trace2)

    print("\n RISULTATI CONFRONTO:")
    for k in results:
        print(f"{k}: {results[k][0]:.3f} sec | {results[k][1]:.3f} MiB")

    labels = list(results.keys())
    durations = [results[k][0] for k in labels]
    memories = [results[k][1] for k in labels]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(labels, memories, color='blue', alpha=0.6, label='Memoria (MiB)')
    ax1.set_ylabel("Memoria (MiB)", color='blue')

    ax2 = ax1.twinx()
    ax2.plot(labels, durations, 'o-', color='red', linewidth=2, label='Tempo (s)')
    ax2.set_ylabel("Tempo (s)", color='red')

    plt.title("MQTT v3: Confronto parsing Scapy vs MQTTP (CONNECT, PUBLISH, SUBSCRIBE)")
    plt.grid(True, linestyle='--', alpha=0.4)
    fig.tight_layout()
    plt.show()
