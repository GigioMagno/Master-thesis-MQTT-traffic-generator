##################################### CLASS #############################################
################################### IO_Handler ##########################################
# CURRENT # 
# This class is necessary to manage IO. This works directly con the attributes of the 
# generator, allowing to fill the devices list and store it in a csv file.

from Model.Generator.Generator import Generator
import pandas as pd

class IO_Handler:
	
	def __init__(self, Gen):
		
		self.Gen = Gen

	


	def load_from_csv_devices_configs(self, csv_path):

		#Default configs for empty fields/rows
		default = {"EmbeddingMethod" : "Case", "QoS" : 0, "Period" : 1.0, "MinRange" : 0.0,
				   "MaxRange" : 1.0, "NumClients" : 1, "Duration" : 10.0, "Distribution" : "uniform",
				   "HiddenMessage" : "", "DeviceType" : "legit", "Protocol" : "MQTTv311", "Retain" : False}

		try:
			df = pd.read_csv(csv_path, sep=";")
			print(df.columns)
			df = df.dropna(subset=["Topic"])
			df = df[df["Topic"] != ""]
			df = df.fillna(default);

			df["QoS"] = df["QoS"].astype(int)
			df["Period"] = df["Period"].astype(float)
			df["MinRange"] = df["MinRange"].astype(float)
			df["MaxRange"] = df["MaxRange"].astype(float)
			df["NumClients"] = df["NumClients"].astype(int)
			df["Duration"] = df["Duration"].astype(float)
			df["Protocol"] = df["Protocol"].astype(str)
			df["Retain"] = df["Retain"].astype(bool)

			self.Gen.devices_configs = df.to_dict("records")

		except Exception as e:
			print("Error during devices configurations from csv:", {e})




	def save_in_csv_devices_configs(self, csv_path):
		
		if self.Gen.devices_configs is not None:
			
			try:
				
				df = pd.DataFrame(self.Gen.devices_configs)
				df.to_csv(csv_path, index = False, sep=";")
				return True

			except Exception as e:
				print("Error while saving")
				return False
		else:
			return False