class MalformedPacketException(Exception):
	
	def __init__(self, message="Malformed packet due to connection errors or the server is not responding anymore"):

		self.message = message
		super().__init__(self.message)