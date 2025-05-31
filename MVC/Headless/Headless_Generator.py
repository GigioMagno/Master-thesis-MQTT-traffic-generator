import sys
import os
import argparse

# Inserisci la root di MVC nel path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from Model.Generator.Generator import Generator
from Controller.Handlers.IO_Handler import IO_Handler

def main():
	
	parser = argparse.ArgumentParser(description="This is MQTT traffic generator")

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-csv", type=str, help="csv pathfile")
	group.add_argument("-pcap", type=str, help="pcap pathfile")

	parser.add_argument("-i", "--interface", type=str, help="Network interface", default="en0")
	parser.add_argument("-b", "--broker", type=str, help="Broker address", default="test.mosquitto.org")
	parser.add_argument("-p", "--port", type=int, help="Port", default=1883)

	args = parser.parse_args()

	print("Parsed args")

	Gen = None


	if args.csv:
		print(f"[CSV MODE]: Selected file {args.csv}")
		Gen = Generator(broker_address=args.broker, port=args.port, interface=args.interface, csv_path=args.csv)
		IO_handler = IO_Handler(Gen)
		IO_handler.load_from_csv_devices_configs(args.csv)
		print("Number of Devices = ", len(Gen.devices_configs))
		Gen.run_generator()

	elif args.pcap:
		print(f"[PCAP MODE]: Selected file {args.pcap}")
		Gen = Generator(broker_address=args.broker, port=args.port, interface=args.interface, csv_path=args.pcap)
		Gen.pcap_simulation()


	
if __name__ == '__main__':
	main()
	exit(21)