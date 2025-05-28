import os, pickle
from scapy.all import rdpcap

# if os.path.exists("packets.pkl"):
#     with open("packets.pkl", "rb") as f:
#         packets = pickle.load(f)
# else:
paths = ["250MB", "500MB", "750MB", "1GB"]
for path in paths:
    savename = path + ".pkl"
    packets = rdpcap(path)
    with open(savename, "wb") as f:
        pickle.dump(packets, f)
