##################################### CLASS #############################################
################################## MQTT_Handler #########################################
# CURRENT # 
# This class manages all the features necessary for MQTT protocol: publish a message,
# subscribe to a topic, check connection, create a MQTT client.

import paho.mqtt.client as mqtt
import threading
import time
from scapy.contrib.mqtt import MQTT, MQTTConnect, MQTTPublish, MQTTSubscribe

class MQTT_handler:	

	def __init__(self, broker_address, port):
	
		self.broker_address = broker_address
		self.port = port
		self.client_lock = threading.Lock()		#Locks management
		self.client_list = []					#list of devices (clients)
		self.working_threads = []



	#Action to perform whenever a subscriber receives a message. This method is required by client object
	def on_message(self, client, userdata, message):
		
		if client._client_id:

			client_id = client._client_id.decode()
		else:

			client_id = "anonymous"

		print(f"Received message '{message.payload.decode()}' from topic '{message.topic}' (Client: '{client_id}')")




	#MQTT client creation
	def mqtt_client(self, client_id=None, timeout=10.0, protocol=mqtt.MQTTv311):
		
		try:
			#client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, transport="websockets")
			client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=protocol)
			client.enable_logger()
			client.on_message = self.on_message
			client.connect(self.broker_address, port=self.port, keepalive=60)
			client.loop_start()

			#timeout = 3.0
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
		
		client = self.mqtt_client(client_id=client_id, protocol=protocol)
		
		if client is not None:
		
			with self.client_lock:
				self.client_list.append(client)
		return client




	#MQTT message publish method: return true iff the message has been sent correctly
	def mqtt_publish_msg(self, publisher, topic, qos, payload):
		
		if publisher is None or not publisher.is_connected():

			print("The publisher does not exists or it is not connected")
			return False

		try:
			
			info = publisher.publish(topic, payload, qos)
			if info.rc == mqtt.MQTT_ERR_SUCCESS:

				print("Message sent")
				return True

		except Exception as e:
			print(f"Error while sending message to {topic}: {e}")
			return False
		return False




	#MQTT topic subscription: return true iff the subscription is successful, false otherwise
	def mqtt_topic_subscription(self, subscriber, topic, qos):
		
		if subscriber is None or not subscriber.is_connected():

			print("The subscriber does not exists or it is not connected")
			return False

		try:
			print("AIUTATEMI VI PREGO")
			info, mid = subscriber.subscribe(topic, qos)
			if info == mqtt.MQTT_ERR_SUCCESS:

				print("Subscription completed")
				return True

		except Exception as e:
			print(f"subscription failed: {e}")
			return False




	#mqtt connection action
	def if_mqtt_connection(self, mqtt_layer, active_clients, protocol):
						
		client_id = mqtt_layer[MQTTConnect].clientId.decode("utf-8", errors="ignore")
		print(f"client_id: {client_id}")
		if client_id not in active_clients or not active_clients[client_id].is_connected():
							
			client = self.mqtt_register_client(client_id, protocol)
			if client:
							
				active_clients[client_id] = client
				return client
		else:

			client = active_clients[client_id]
			return client




	#mqtt publishing action
	def if_mqtt_publish(self, mqtt_layer, active_clients):
		
		last_client = None
		print(f"QUA ENTRO: Active clients: {active_clients}")
		if active_clients:

			last_client = list(active_clients.values())[-1]
			print(f"last_client {last_client}")			

		if last_client:

			mqtt_publish = mqtt_layer[MQTTPublish]
			topic = mqtt_publish.topic.decode("utf-8", errors="ignore")
			qos = mqtt_layer.QOS
			payload = mqtt_publish.value
			self.mqtt_publish_msg(last_client, topic, qos, payload)
			print(f"Pubblico su Topic' {topic} con payload {payload}")

			return last_client
		
		return None




	#mqtt subscription action
	def if_mqtt_subscription(self, mqtt_layer, active_clients):
		
		subscriber = None

		if active_clients:
			
			subscriber = list(active_clients.values())[-1]

		if subscriber:
			
			mqtt_subscribe = mqtt_layer[MQTTSubscribe]		
			for subscription_topic in mqtt_subscribe.topics:

				topic = subscription_topic[0].decode("utf-8", errors="ignore")
				qos = subscription_topic[1]
				print(f"quality of service subscriber {qos}")
				self.mqtt_topic_subscription(subscriber, topic, qos)

			return subscriber

		return None




	#mqtt disconnection action
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