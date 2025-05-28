#Read from a csv, enlarge the payload, save the csv

import pandas as pd

def read_payload(path):
	with open(path) as f:
		txt = f.read()
		return txt



#Default case values
default = {"EmbeddingMethod" : "Case", "QoS" : 0, "Period" : 1.0, "MinRange" : 0.0,
				   "MaxRange" : 1.0, "NumClients" : 1, "Duration" : 10.0, "Distribution" : "uniform",
				   "HiddenMessage" : "", "DeviceType" : "legit", "Protocol" : "MQTTv311", "Retain" : False}


csv_path = "/Users/svitol/Desktop/WIP/TESI/Traffic_Generator/Master-thesis-MQTT-traffic-generator/MVC/Headless/quadDos.csv"
payload_path = "/Users/svitol/Desktop/WIP/TESI/Traffic_Generator/Master-thesis-MQTT-traffic-generator/MVC/Headless/file_50mb.txt"
save_path = "/Users/svitol/Desktop/WIP/TESI/Traffic_Generator/Master-thesis-MQTT-traffic-generator/MVC/Headless/quadDosHeavyPyaload.csv"

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
	df["Payload"] = read_payload(payload_path)
except:

	print("Malformed record")


df.to_csv(save_path, index = False, sep=";")