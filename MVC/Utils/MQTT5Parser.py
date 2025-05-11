##################################### CLASS #############################################
################################## MQTT5PARSER ##########################################
# CURRENT # 
# This class is designed to parse MQTTv5 packets according to their structure:
# https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901019
# A customized parser has been written for the principal packets: publish, subscribe 
# and connect. There's also a client_id parser and a dispatcher function (not used for
# the moment)


class MQTT5Parser:

	packets_type = {
		1:"CONNECT", 2:"CONNACK", 3:"PUBLISH", 4:"PUBACK",
		5:"PUBREC", 6:"PUBREL", 7:"PUBCOMP", 8:"SUBSCRIBE",
		9:"SUBACK", 10:"UNSUBSCRIBE", 11:"UNSUBACK", 12:"PINGREQ",
		13:"PINGRESP", 14:"DISCONNECT", 15:"AUTH"
	}



	# Decorder for VBI
	@staticmethod
	def decode_variable_byte_integer(data, start_index):

		multiplier = 1
		value = 0
		index = start_index

		while True:
			byte = data[index]
			value += (byte & 127) * multiplier
			index += 1
			if (byte & 128) == 0:

				break
			multiplier *= 128
		
		return value, index



	#SUBSCRIBE PACKET PARSER
	@staticmethod
	def parse_subscribe_payload(raw_bytes):

		#print(f"RAWBYTES PACKETS: {bytes(raw_bytes)}")
		packet_type = (raw_bytes[0] >> 4) & 0x0F
		if packet_type != 8:

			raise ValueError(f"Pacchetto non SUBSCRIBE type {packet_type}")

		remaining_len, idx_after_rl = MQTT5Parser.decode_variable_byte_integer(raw_bytes, 1)
		packet_id = int.from_bytes(raw_bytes[idx_after_rl:idx_after_rl+2], "big")
		idx = idx_after_rl + 2

		prop_len, idx_after_pl = MQTT5Parser.decode_variable_byte_integer(raw_bytes, idx)
		idx = idx_after_pl + prop_len

		topic_len = int.from_bytes(raw_bytes[idx:idx+2], "big")
		idx += 2
		topic = raw_bytes[idx:idx+topic_len].decode("utf-8", errors="ignore")
		idx += topic_len

		subscription_options = raw_bytes[idx]
		qos = subscription_options & 0x03

		return packet_id, [(topic, qos)]



	#PUBLISH PACKET PARSER
	@staticmethod
	def parse_publish_payload(raw_bytes):

		remaining_len, idx_after_rl = MQTT5Parser.decode_variable_byte_integer(raw_bytes, 1)
		idx = idx_after_rl

		topic_len = int.from_bytes(raw_bytes[idx:idx+2], 'big')
		idx += 2
		topic = raw_bytes[idx:idx+topic_len].decode('utf-8', errors='ignore')
		idx += topic_len

		qos = (raw_bytes[0] & 0b00000110) >> 1
		if qos > 0:
			idx += 2  # skip packet identifier

		prop_len, idx_after_pl = MQTT5Parser.decode_variable_byte_integer(raw_bytes, idx)
		idx = idx_after_pl + prop_len

		payload = raw_bytes[idx:]

		return topic, qos, payload



	#CONNECT PACKET PARSER
	@staticmethod
	def parse_connect_info(raw_bytes):

		if (raw_bytes[0] >> 4) & 0x0F != 1:

			raise ValueError("Non è un pacchetto CONNECT")
		# Decode Remaining Length e individua offset del variable header
		_, offset = MQTT5Parser.decode_variable_byte_integer(raw_bytes, 1)
		
		proto_name_len = int.from_bytes(raw_bytes[offset:offset+2], "big")
		proto_name = raw_bytes[offset+2:offset+2+proto_name_len].decode("utf-8", errors="ignore")
		proto_level = raw_bytes[offset+2+proto_name_len]

		return {
			"protocol_name": proto_name,
			"protocol_level": proto_level
		}



	#CLIENT ID PARSER
	@staticmethod
	def extract_client_id(raw_bytes):

		_, offset = MQTT5Parser.decode_variable_byte_integer(raw_bytes, 1)
		proto_name_len = int.from_bytes(raw_bytes[offset:offset+2], "big")
		idx = offset + 2 + proto_name_len + 1 + 1 + 2  # + proto_level + connect_flags + keepalive
		prop_len, prop_end = MQTT5Parser.decode_variable_byte_integer(raw_bytes, idx)
		idx = prop_end + prop_len
		client_id_len = int.from_bytes(raw_bytes[idx:idx+2], "big")
		idx += 2
		client_id = raw_bytes[idx:idx+client_id_len].decode("utf-8", errors="ignore")

		return client_id



	#Dispatcher not used for the moment but could be useful
	@staticmethod
	def dispatch_parser(raw_bytes):
		packet_type = (raw_bytes[0] >> 4) & 0x0F
		print(f"[DISPATCH] Tipo pacchetto MQTT 5: {MQTT5Parser.packets_type.get(packet_type, 'UNKNOWN')}")

		try:
			if packet_type == 3:

				return MQTT5Parser.parse_publish_payload(raw_bytes)
			elif packet_type == 8:

				return MQTT5Parser.parse_subscribe_payload(raw_bytes)
			elif packet_type == 1:

				return MQTT5Parser.parse_connect_info(raw_bytes)
			else:

				print(f"[WARNING] Nessun parser implementato per packet type {packet_type}")
				return None
		except Exception as e:
			print(f"[ERROR] Parsing fallito per tipo {packet_type}: {e}")
			return None