##################################### CLASS #############################################
################################## MQTT_Handler #########################################
# CURRENT # 
# This class manages all the features necessary for MQTT protocol: publish a message,
# subscribe to a topic, check connection, create a MQTT client.

import paho.mqtt.client as mqtt
import threading
import time
#from scapy.contrib.mqtt import MQTT, MQTTConnect, MQTTPublish, MQTTSubscribe
from Utils.MQTTP import MQTTv5Parser, MQTTv3Parser
from Utils.MalformedPacketException import MalformedPacketException

class MQTT_handler:	

	def __init__(self, broker_address, port):
	
		self.broker_address = broker_address
		self.port = port
		self.client_lock = threading.Lock()		#Locks management
		self.client_list = []					#list of devices (clients)
		self.working_threads = []
		self.client_protocols = {}


	#In condizioni normali (no DOS)

	#Action to perform whenever a subscriber receives a message. This method is required by client object
	# def on_message(self, client, userdata, message):
		
	# 	if client._client_id:

	# 		client_id = client._client_id.decode()
	# 	else:

	# 		client_id = "anonymous"

#Da attivare per attacco dos alla cpu

	def on_message(self, client, userdata, message):
		#Da rimuovere se creano problemi
		del message
		del userdata
		pass


		#print(f"Received message '{message.payload.decode()}' from topic '{message.topic}' (Client: '{client_id}')")



	#MQTT client creation
	def mqtt_client(self, client_id=None, timeout=10.0, protocol=mqtt.MQTTv311):
		
		try:
			#Per fare clean_session su mqtt 3.1.1
			#client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=protocol, clean_session=False)
			client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=protocol)
			client.enable_logger()
			client.on_message = self.on_message
			client.connect(self.broker_address, port=self.port, keepalive=60)
			client.loop_start()

			while not client.is_connected() and timeout > 0:
				time.sleep(0.1)
				timeout -= 0.1

			if not client.is_connected():
				
				print(f"MQTT client {client_id} cannot establish the connection")
				return None

			return client
		
		except Exception as e:
			print("MQTT client connection error ", {e})
			return None



	#MQTT client registration: each client logs itself in thread/client list		
	def mqtt_register_client(self, client_id=None, protocol=mqtt.MQTTv311):
		
		client_id = client_id or ""
		client = self.mqtt_client(client_id=client_id, protocol=protocol)
		print(f"[DEBUG] Registrato client_id={client_id} con protocol={protocol}")		
		if client is not None:
		
			with self.client_lock:
				self.client_list.append(client)

			self.client_protocols[client_id] = protocol

		return client



	#MQTT message publish method: return true iff the message has been sent correctly. Retain can be either true or false
	def mqtt_publish_msg(self, publisher, topic, qos, payload, retain):

		try:
			
			info = publisher.publish(topic, payload, qos, retain=retain)
			if info.rc == mqtt.MQTT_ERR_SUCCESS:

				del info
				#print("Message sent")
				return True

		except Exception as e:
			#print(f"Error while sending message to {topic}: {e}")
			return False
		return False



	#MQTT topic subscription: return true iff the subscription is successful, false otherwise
	def mqtt_topic_subscription(self, subscriber, topic, qos):
		
		if subscriber is None or not subscriber.is_connected():

			#print("The subscriber does not exists or it is not connected")
			return False

		try:

			info, mid = subscriber.subscribe(topic, qos)
			if info == mqtt.MQTT_ERR_SUCCESS:

				print("Subscription completed")
				return True

		except Exception as e:
			print(f"subscription failed: {e}")
			return False



	#mqtt connection action
	#@profile
	def if_mqtt_connection(self, mqtt_layer, active_clients, protocol):
		
		#raw = bytes(mqtt_layer)

		try:

			if protocol == 5:
				
				client_id, protocol_level, ProtocolName = MQTTv5Parser.ParseConnectPacket(mqtt_layer)
				#print(f"Decoded CONNECT packet using my parser for MQTTv5 -> ClientID: {client_id}, PROTOCOLNAME: {ProtocolName}, PROTOCOL_LEVEL: {protocol_level}")
			else:

				client_id, protocol_level, ProtocolName = MQTTv3Parser.ParseConnectPacket(mqtt_layer)
				#print(f"Decoded CONNECT packet using my parser for MQTTv3 -> ClientID: {client_id}, PROTOCOLNAME: {ProtocolName}, PROTOCOL_LEVEL: {protocol_level}")

		except MalformedPacketException as e:

			return None
			#raise MalformedPacketException(f"MalformedPacketException for client {client_id}") from e

		except Exception as e:
			
			return None
			#raise Exception(f"Unexpected error parsing MQTT Connection packet for client {client_id}") from e
			#protocol_level = protocol
			#client_id = ""

		#print(f"CONNECTED WITH CLIENT_ID: {client_id}")

		if client_id not in active_clients or not active_clients.get(client_id, None) or not active_clients[client_id].is_connected():

			client = self.mqtt_register_client(client_id, protocol)
			if client:

				self.client_protocols[client_id] = protocol
				active_clients[client_id] = client
				return client
		else:

			return active_clients[client_id]



	#mqtt publishing action
	def if_mqtt_publish(self, mqtt_layer, active_clients, retain):
		
		last_client = None

		if active_clients:

			last_client = list(active_clients.values())[-1]		

		if last_client:

			client_id = last_client._client_id.decode("utf-8", errors="ignore") if last_client._client_id else ""
			protolevel = self.client_protocols.get(client_id, 4)

			try:
				if protolevel == 5:

					qos, topic, PacketID, payload = MQTTv5Parser.ParsePublishPacket(mqtt_layer)
					#print(f"Decoded PUBLISH using my parser for MQTTv5 -> QoS: {qos}, TOPIC: {topic}, PACKETID: {PacketID}, PAYLOAD: {payload}")

				else:
					
					qos, topic, PacketID, payload = MQTTv3Parser.ParsePublishPacket(mqtt_layer)
					#print(f"Decoded PUBLISH using my parser for MQTTv3 -> QoS: {qos}, TOPIC: {topic}, PACKETID: {PacketID}, PAYLOAD: {payload}")
				

				if last_client is not None and last_client.is_connected():
					
					self.mqtt_publish_msg(last_client, topic, qos, payload, retain)
					#print(f"Pubblico su Topic' {topic} con payload {payload}")

				return last_client

			except MalformedPacketException as e:

				#raise MalformedPacketException(f"MalformedPacketException for client {client_id}") from e
				return None

			except Exception as e:

				#raise Exception(f"Unexpected error parsing MQTT Publish packet for client {client_id}") from e
				return None

		return None





	#mqtt subscription action -> prints are kept for debugging
	def if_mqtt_subscription(self, mqtt_layer, active_clients):
		
		subscriber = None

		if active_clients:
			
			subscriber = list(active_clients.values())[-1]

		if subscriber:
			
			client_id = subscriber._client_id.decode("utf-8", errors="ignore") if subscriber._client_id else ""
			protolevel = self.client_protocols.get(client_id, 4)	#default case MQTT3.1.1

			try:

				if protolevel == 5:
					
					packet_id, topics = MQTTv5Parser.ParseSubscribePacket(mqtt_layer)

				else:
				
					packet_id, topics = MQTTv3Parser.ParseSubscribePacket(mqtt_layer)

				for topic, qos in topics:
					#print(f"Decoded SUBSCRIBE packet using my parser for MQTT -> PACKET ID: {packet_id}, TOPIC: {topic}, QoS: {qos}")
					self.mqtt_topic_subscription(subscriber, topic, qos)
			
			except MalformedPacketException as e:

				#raise MalformedPacketException(f"MalformedPacketException for client {client_id}") from e
				return None
			
			except Exception as e:

				#print(f"MQTT SUBSCRIPTION ERROR, CHECK PARSER AND PACKETS: {e}")
				#raise Exception(f"Unexpected error parsing MQTT subscription packet for client {client_id}") from e
				return None

			return subscriber

		return None



	#mqtt disconnection action -> rimuovere mqtt_layer. Non serve
	def if_mqtt_disconnection(self, mqtt_layer, active_clients):
		
		if active_clients:
			
			last_client_id = list(active_clients.keys())[-1]
			client_to_disconnect = active_clients.pop(last_client_id, None)

			if client_to_disconnect:

				with self.client_lock:
					if client_to_disconnect in self.client_list:

						self.client_list.remove(client_to_disconnect)
					client_to_disconnect.disconnect()
					client_to_disconnect.loop_stop()