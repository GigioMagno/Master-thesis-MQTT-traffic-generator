from abc import ABC, abstractmethod
#This is an MQTTv5 and MQTTv3* packet parser

class MQTTParser(ABC):
	
	#idx represents the pointer to the first byte of of the variable length quantity
	@staticmethod
	def VLFDecode(RawBytes, idx):
		
		start_idx = idx
		#partials = [] #contain the partial numbers encoded in each byte, the position in the list corresponds to the weigth that is assigned to each partial
		VLI = 0 #VLI = Variable length integer
		multiplier = 1
		while True:	#I prefer put the stop condition here and then repeat a small piece of code, in order to not encounter the if construct at each iteration (if instead of the condition i put while True)
			
			byte = RawBytes[idx]
			VLI += (byte & 0x7F) * multiplier
			idx += 1
			multiplier *= 128
			if byte & 0x80 == 0:
				
				break

		#Return the variable length integer and the number of bytes
		return VLI, idx-start_idx
	#This function works in general, but in MQTT case at most 4 bytes can be read

	#VLFBytes is the number of bytes for Variable Length Field

	@staticmethod
	def ParseProtocol(MQTT5_layer):
		
		raw_layer = bytes(MQTT5_layer)
		idx = 1
		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)

		#Variable header processing
		#pointer to the first byte of the variable header
		idx += VLFBytes
		ProtocolNameLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2 #pointer to the first byte of the name of the protocol
		ProtocolName = str(raw_layer[idx:idx+ProtocolNameLength], "utf-8")
		idx += ProtocolNameLength
		ProtocolLevel = raw_layer[idx]	#5 expected for MQTTv5
		
		return ProtocolName, ProtocolLevel

	
	@staticmethod
	@abstractmethod
	def ParseConnectPacket():
		pass
	
	@staticmethod
	@abstractmethod
	def ParsePublishPacket():
		pass
	
	@staticmethod
	@abstractmethod
	def ParseSubscribePacket():
		pass







class MQTTv5Parser(MQTTParser):



	@staticmethod
	def ParseConnectPacket(MQTT5_layer):
		
		raw_layer = bytes(MQTT5_layer)

		#Fixed header processing
		IsConnected = raw_layer[0] & 0xF0
		IsMalformed = raw_layer[0] & 0x0F

		if IsConnected != 0x10 or IsMalformed != 0x00:
			
			print("Not CONNECT packet or Malformed packet")

		idx = 1
		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)

		#Variable header processing
		#pointer to the first byte of the variable header
		idx += VLFBytes
		ProtocolNameLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2 #pointer to the first byte of the name of the protocol
		ProtocolName = str(raw_layer[idx:idx+ProtocolNameLength], "utf-8")
		idx += ProtocolNameLength
		ProtocolLevel = raw_layer[idx]	#5 expected for MQTTv5
		idx += 1
		ConnectionFlags = raw_layer[idx]	#connection configs 
		idx += 1
		KeepAlive = int.from_bytes(raw_layer[idx:idx+2], "big")	#Timeout in milliseconds
		idx += 2
		PropertiesBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes
		idx += PropertiesBytes

		#Payload Processing
		ClientIDLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2
		ClientID = str(raw_layer[idx:idx+ClientIDLength], "utf-8")

		return (ClientID, ProtocolLevel, ProtocolName)



	@staticmethod
	def ParsePublishPacket(MQTT5_layer):
		
		raw_layer = bytes(MQTT5_layer)

		#Fixed header processing
		IsPublish = raw_layer[0] & 0xF0
		PublishProperties = raw_layer[0] & 0x0F

		if IsPublish != 0x30:
			print("No PUBLISH packet or Malformed packet")

		QoS = (PublishProperties & 0x06) >> 1

		if QoS == 3:
			print(f"Malformed packet: {QoS}")

		DupFlag = (PublishProperties & 0x08) >> 3
		RetainFlag = PublishProperties & 0x01
		
		idx = 1
		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes

		#Variable header
		TopicNameLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2
		Topic = str(raw_layer[idx:idx+TopicNameLength], "utf-8")
		idx += TopicNameLength
		PacketID = None
		if QoS > 0:
		
			PacketID = int.from_bytes(raw_layer[idx:idx+2], "big")
			idx += 2

		PropertiesBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)

		idx += VLFBytes
		idx += PropertiesBytes

		#Payload
		#Controllare se è necessario mettere indice di fine, credo di no.
		Payload = str(raw_layer[idx:], "utf-8")

		return (QoS, Topic, PacketID, Payload)


	@staticmethod
	def ParseSubscribePacket(MQTT5_layer):
		
		raw_layer = bytes(MQTT5_layer)

		#Fixed Header
		IsSubscribe = raw_layer[0] & 0xF0
		Flags = raw_layer[0] & 0x0F
		idx = 1
		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes
		TotalPacketLength = idx + RemainingBytes
		#Variable Header
		PacketID = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2
		PropertiesBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes
		idx += PropertiesBytes

		Topics = []
		SubscriptionOptions = []
		QoSs = []	#Quality of Service(s) -> this explain the final s
		TopicQos = []
		#Payload
		while idx < TotalPacketLength:

			TopicLength = int.from_bytes(raw_layer[idx:idx+2], "big")
			idx += 2
			Topic = str(raw_layer[idx:idx+TopicLength], "utf-8")
			Topics.append(Topic)
			idx += TopicLength
			SubscriptionOptions.append(raw_layer[idx])	#Save the byte that contains Subscription options
			QoS = raw_layer[idx] & 0x03
			QoSs.append(QoS)
			idx += 1
			TopicQos.append((Topic, QoS))

		return (PacketID, TopicQos)
		#return {"PacketID":PacketID, ("QoSs":QoSs, "Topics":Topics)}





class MQTTv3Parser(MQTTParser):


	@staticmethod
	def ParseConnectPacket(MQTT3_layer):
		
		raw_layer = bytes(MQTT3_layer)
		idx = 1

		#Fixed header processing
		IsConnected = raw_layer[0] & 0x10
		IsMalformed = raw_layer[0] & 0x0F

		if IsConnected != 0x10 or IsMalformed != 0x00:
			
			print("Not CONNECT packet or Malformed packet")

		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes

		#Variable header processing
		ProtocolNameLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2
		ProtocolName = str(raw_layer[idx:idx+ProtocolNameLength], "utf-8")
		idx += ProtocolNameLength
		ProtocolLevel = int.from_bytes(raw_layer[idx:idx+1], "big")	#3-4 for mqtt3 and mqtt3.1.1
		idx += 1
		BitField = raw_layer[idx]
		idx += 1
		KeepAlive = int.from_bytes(raw_layer[idx:idx+2], "big")	#Timeout in milliseconds
		idx += 2
		
		#Payload
		ClientIDLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2
		ClientID = str(raw_layer[idx:idx+ClientIDLength], "utf-8")
		idx += ClientIDLength
		#Continue with will fields... it is quite different from v5

		return (ClientID, ProtocolLevel, ProtocolName)



	@staticmethod
	def ParsePublishPacket(MQTT3_layer):
		
		raw_layer = bytes(MQTT3_layer)
		idx = 1

		#Fixed Header
		IsPublish = raw_layer[0] & 0xF0
		PublishProperties = raw_layer[0] & 0x0F
		DupFlag = PublishProperties >> 3
		QoS = (PublishProperties & 0x06) >> 1
		RetainFlag = PublishProperties & 0x01

		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes

		#Variable Header
		TopicNameLength = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2
		Topic = str(raw_layer[idx:idx+TopicNameLength], "utf-8")
		idx += TopicNameLength

		PacketID = None
		
		if QoS > 0:
			
			PacketID = int.from_bytes(raw_layer[idx:idx+2], "big")
			idx +=2

		#Payload
		Payload = str(raw_layer[idx:], "utf-8")

		return (QoS, Topic, PacketID, Payload)



	@staticmethod
	def ParseSubscribePacket(MQTT3_layer):
		
		raw_layer = bytes(MQTT3_layer)
		idx = 1

		#Fixed Header
		IsSubscribe = raw_layer[0] & 0xF0
		Flags = raw_layer[0] & 0x0F
		
		if IsSubscribe != 0x80 or Flags != 0x02:

			print("Not SUBSCRIBE packet or Malformed packet")

		RemainingBytes, VLFBytes = MQTTParser.VLFDecode(raw_layer, idx)
		idx += VLFBytes
		TotalPacketLength = idx + RemainingBytes

		#Variable Header
		PacketID = int.from_bytes(raw_layer[idx:idx+2], "big")
		idx += 2

		
		#Payload
		TopicQos = []
		while idx < TotalPacketLength:
			
			TopicLength = int.from_bytes(raw_layer[idx:idx+2], "big")
			idx += 2
			Topic = str(raw_layer[idx:idx+TopicLength], "utf-8")
			idx += TopicLength
			QoS = raw_layer[idx]
			TopicQos.append((Topic, QoS))
			idx += 1	


		return (PacketID, TopicQos)