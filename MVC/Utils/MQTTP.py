# ##################################### CLASS #############################################
# ##################################### MQTTP #############################################
# # CURRENT # 
# # This script contains three classes. One of them (MQTTParser) is an abstract class and 
# # is used as root for the other two. The other two classes (MQTTv5Parser & MQTTv3Parser)
# # are derived from MQTTParser and implements specific parsing methods according to the
# # protocol specifications.

from abc import ABC, abstractmethod
from Utils.MalformedPacketException import MalformedPacketException

class MQTTParser(ABC):



	@staticmethod
	def VLFDecode(raw, idx):

		start = idx
		value = 0
		multiplier = 1

		while True:
			byte = raw[idx]
			value += (byte & 0x7F) * multiplier
			idx += 1
			if byte & 0x80 == 0:

				break
			multiplier *= 128

		return value, idx - start



	@staticmethod
	def ParseProtocol(raw):

		if not isinstance(raw, bytes):

			raw = bytes(raw)
		
		idx = 1
		_, vlf_len = MQTTParser.VLFDecode(raw, idx)
		idx += vlf_len
		name_len = (raw[idx] << 8) | raw[idx+1]
		idx += 2
		name = raw[idx:idx+name_len].decode("utf-8")
		idx += name_len
		level = raw[idx]

		return name, level



	@staticmethod
	@abstractmethod
	def ParseConnectPacket(raw):
		pass



	@staticmethod
	@abstractmethod
	def ParsePublishPacket(raw):
		pass



	@staticmethod
	@abstractmethod
	def ParseSubscribePacket(raw):
		pass





class MQTTv5Parser(MQTTParser):



	@staticmethod
	def ParseConnectPacket(raw):

		if not isinstance(raw, bytes):
			raw = bytes(raw)
		if (raw[0] & 0xF0 != 0x10) or (raw[0] & 0x0F != 0x00):
			return (None, None, None)

		try:
			idx = 1
			_, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len
			proto_len = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			proto_name = raw[idx:idx+proto_len].decode("utf-8")
			idx += proto_len
			proto_level = raw[idx]
			idx += 4  # skip ConnectionFlags and KeepAlive (2 bytes)
			props_len, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len + props_len
			client_len = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			client_id = raw[idx:idx+client_len].decode("utf-8")

			return (client_id, proto_level, proto_name)

		except Exception:

			raise MalformedPacketException()



	@staticmethod
	def ParsePublishPacket(raw):

		if not isinstance(raw, bytes):
			raw = bytes(raw)
		if raw[0] & 0xF0 != 0x30:
			raise MalformedPacketException()

		qos = (raw[0] & 0x06) >> 1
		if qos > 2: 
			raise MalformedPacketException()

		try:
			idx = 1
			_, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len
			topic_len = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			topic = raw[idx:idx+topic_len].decode("utf-8")
			idx += topic_len
			packet_id = None
			if qos > 0:
				packet_id = (raw[idx] << 8) | raw[idx+1]
				idx += 2
			prop_len, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len + prop_len
			payload = raw[idx:].decode("utf-8")
			return (qos, topic, packet_id, payload)

		except Exception:

			raise MalformedPacketException()



	@staticmethod
	def ParseSubscribePacket(raw):

		if not isinstance(raw, bytes):

			raw = bytes(raw)
		try:
			if raw[0] & 0xF0 != 0x82:

				return (None, None)
			idx = 1
			rem_len, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len
			end = idx + rem_len
			packet_id = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			prop_len, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len + prop_len
			topic_qos = []

			while idx < end:

				topic_len = (raw[idx] << 8) | raw[idx+1]
				idx += 2
				topic = raw[idx:idx+topic_len].decode("utf-8")
				idx += topic_len
				qos = raw[idx] & 0x03
				idx += 1
				topic_qos.append((topic, qos))

			return (packet_id, topic_qos)

		except Exception:

			raise MalformedPacketException()


class MQTTv3Parser(MQTTParser):



	@staticmethod
	def ParseConnectPacket(raw):

		if not isinstance(raw, bytes):
			
			raw = bytes(raw)
		if (raw[0] & 0xF0 != 0x10) or (raw[0] & 0x0F != 0x00):
			
			return (None, None, None)
		try:
			idx = 1
			_, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len
			proto_len = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			proto_name = raw[idx:idx+proto_len].decode("utf-8")
			idx += proto_len
			proto_level = raw[idx]
			idx += 3  # skip BitField + KeepAlive (2 bytes)
			client_len = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			client_id = raw[idx:idx+client_len].decode("utf-8")
			return (client_id, proto_level, proto_name)

		except Exception:

			raise MalformedPacketException()



	@staticmethod
	def ParsePublishPacket(raw):

		if not isinstance(raw, bytes):

			raw = bytes(raw)
		try:
			idx = 1
			_, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len
			topic_len = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			topic = raw[idx:idx+topic_len].decode("utf-8")
			idx += topic_len
			qos = (raw[0] & 0x06) >> 1
			packet_id = None
			if qos > 0:

				packet_id = (raw[idx] << 8) | raw[idx+1]
				idx += 2
			payload = raw[idx:].decode("utf-8")
			return (qos, topic, packet_id, payload)

		except Exception:

			raise MalformedPacketException()



	@staticmethod
	def ParseSubscribePacket(raw):

		if not isinstance(raw, bytes):
			
			raw = bytes(raw)
		if raw[0] & 0xF0 != 0x80:
			
			return (None, None)
		try:
			idx = 1
			rem_len, vlf_len = MQTTParser.VLFDecode(raw, idx)
			idx += vlf_len
			end = idx + rem_len
			packet_id = (raw[idx] << 8) | raw[idx+1]
			idx += 2
			topic_qos = []

			while idx < end:

				topic_len = (raw[idx] << 8) | raw[idx+1]
				idx += 2
				topic = raw[idx:idx+topic_len].decode("utf-8")
				idx += topic_len
				qos = raw[idx]
				idx += 1
				topic_qos.append((topic, qos))
			return (packet_id, topic_qos)

		except Exception:

			raise MalformedPacketException()