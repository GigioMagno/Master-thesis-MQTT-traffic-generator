##################################### CLASS #############################################
################################## NET_SNIFFER ##########################################
# CURRENT # 
# This class contains two method: the first runs tshark to capture packets on the network
# the second stops the capture. The capture is started as a new sub process.

import subprocess, os, signal
import time
from datetime import datetime


class NetSniffer:
	
	def __init__(self, port=443, interface="en0"):
		
		self.capture_process = None
		self.port = port
		self.interface = interface



	def run_tshark(self):
		
		if self.capture_process is None:				#if no capture_process is running...
														#start a new capture_process process
			try:
				self.capture_process = subprocess.Popen(["tshark", "-i", f"{self.interface}", "-f", f"tcp port {self.port}", "-w", f"generated_traffic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pcap"], preexec_fn=os.setsid)
				print(f"La porta è: {self.port}")
				print(["COMMAND:", "tshark", "-i", f"{self.interface}", "-f", f"tcp port {self.port}", "-w", f"generated_traffic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pcap"])
				#self.capture_process = subprocess.Popen(["tshark", "-i", "en0", "-f", f"port {self.port}", "-w", f"generated_traffic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pcap"], preexec_fn=os.setsid)
				#self.capture_process = subprocess.Popen(["tshark", "-i", "en0", "-w", f"generated_traffic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pcap"], preexec_fn=os.setsid)
				print(f"Reference process: {self.capture_process}")
			except Exception as e:
				print(f"Error running tshark: {e}")
				self.capture_process = None
		else:
			print("tshark is running...")
			return




	def stop_tshark(self):

		if self.capture_process is not None:			#if there's a capture_process process running...
														#terminate it, but if it doesn't terminate within 5 secs, kill it
			try:
				print("Killing tshark")
				os.killpg(os.getpgid(self.capture_process.pid), signal.SIGTERM)
				self.capture_process.wait(timeout=5)
				print("Killed tshark")
			
			except subprocess.TimeoutExpired:
				os.killpg(os.getpgid(self.capture_process.pid), signal.SIGKILL)
				print("Killed tshark")

			except Exception:

				print("tshark crashed")
			
			self.capture_process = None