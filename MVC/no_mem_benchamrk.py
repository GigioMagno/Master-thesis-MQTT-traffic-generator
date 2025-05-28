import mmap
import time
import sys
import io
import matplotlib.pyplot as plt
from memory_profiler import memory_usage
from scapy.all import rdpcap, TCP
from scapy.contrib.mqtt import MQTT
from Utils.MQTTP import MQTTv3Parser

def load_pcap_with_mmap(path):
    with open(path, "rb") as f:
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
            return rdpcap(io.BytesIO(mm.read()))

def extract_mqtt3_packets(packets):
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
            _ = pkt[MQTT]
        except Exception:
            pass

def run_custom_parser(packets):
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
    print(f"\nCaricamento pacchetti MQTT v3 da {pcap_file} con mmap...")

    all_packets = load_pcap_with_mmap(pcap_file)
    mqtt3_packets = extract_mqtt3_packets(all_packets)
    print(f"Trovati {len(mqtt3_packets)} pacchetti MQTT v3")

    if len(mqtt3_packets) == 0:
        print("Nessun pacchetto MQTT v3 trovato.")
        sys.exit(0)

    results = {}

    dur, mem, trace2 = benchmark("Parsing con la MQTTP", run_custom_parser, mqtt3_packets)
    results["MQTTP"] = (dur, mem, trace2)

    dur, mem, trace1 = benchmark("Parsing con Scapy", run_scapy_parser, mqtt3_packets)
    results["Scapy"] = (dur, mem, trace1)

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

    plt.title("MQTT v3: Confronto parsing MQTTP vs Scapy")
    plt.grid(True, linestyle='--', alpha=0.4)
    fig.tight_layout()
    plt.show()
