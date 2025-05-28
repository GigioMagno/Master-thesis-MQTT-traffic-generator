import pickle, os
from scapy.contrib.mqtt import MQTT
from scapy.all import TCP
import time, sys
from memory_profiler import memory_usage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from Utils.MQTTP import MQTTv3Parser


def ScapyParserTesterFunction(packets):
	
	for packet in packets:
		try:
			_ = pkt[MQTT]
		except Exception as e:
			continue




def MQTTParserTesterFunction(packets):

	for packet in packets:
		try:
			raw = bytes(pkt[TCP].payload)
			msg_type = raw[0] & 0xF0
			if msg_type == 0x10:
				
				MQTTv3Parser.ParseConnectPacket(raw)
			elif msg_type == 0x30:

				MQTTv3Parser.ParsePublishPacket(raw)

			elif msg_type == 0x80:

				MQTTv3Parser.ParseSubscribePacket(raw)
			else:
				continue
		except Exception as e:
			continue




def TestLibs(name, function, packets):
	
	print(f"{name}")
	start = time.time()
	memory = memory_usage((function, (packets, )), interval=0.05)
	end = time.time()

	duration = end - start
	peak = max(memory)- min(memory)

	return duration, peak, memory




if __name__ == '__main__':
	
	
	picklePath = "/Users/svitol/Desktop/WIP/TESI/Traffic_Generator/Master-thesis-MQTT-traffic-generator/MVC/GeneratedTraffic/750MB.pkl"

	with open(picklePath, "rb") as f:
		Packets = pickle.load(f)

	
	duration, peak, memory = TestLibs("MQTTP", MQTTParserTesterFunction, Packets)
	print(f"MQTTP performance evaluation:\n Duration: {duration}\n Peak: {peak}\n Memory: {memory}")


	duration, peak, memory = TestLibs("Scapy", ScapyParserTesterFunction, Packets)
	print(f"Scapy performance evaluation:\n Duration: {duration}\n Peak: {peak}\n Memory: {memory}")