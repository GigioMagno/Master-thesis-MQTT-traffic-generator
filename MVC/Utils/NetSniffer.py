import subprocess, os, signal
import time
from datetime import datetime


class NetSniffer:
	
	def __init__(self, port=443):
		
		self.capture_process = None
		self.port = port


	############################### TSHARK START AND STOP ####################################

	# RUN TSHARK CAPTURE PROCESS
	def run_tshark(self):
		
		if self.capture_process is None:				#if no capture_process is running...
														#start a new capture_process process
			try:
				self.capture_process = subprocess.Popen(["tshark", "-i", "en0", "-f", f"tcp port {self.port}", "-w", f"generated_traffic_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pcap"], preexec_fn=os.setsid)
				print(f"Reference process: {self.capture_process}")
			except Exception as e:
				print("Error running tshark")
				self.capture_process = None
		else:
			print("tshark is running...")
			return
			
	# STOP TSHARK CAPTURE PROCESS
	def stop_tshark(self):

		if self.capture_process is not None:			#if there's a capture_process process running...
														#terminate it, but if it doesn't terminate within 5 secs, kill it
			try:
				print("Provo a killare il processo...")
				os.killpg(os.getpgid(self.capture_process.pid), signal.SIGTERM)
				print("Do 5 secondi al processo...")
				self.capture_process.wait(timeout=5)
				print("Ho killato il processo...")
			
			except subprocess.TimeoutExpired:
				print("Devo killare il processo...")
				os.killpg(os.getpgid(self.capture_process.pid), signal.SIGKILL)
				print("processo killato")

			except Exception:

				print("tshark crashed")
			
			self.capture_process = None
	
