from twisted.internet import protocol, reactor

class MyProtocol(protocol.Protocol):
	def __init__(self, factory):
		self.factory = factory
		self.nickname = "ANONYMOUS"
	def connectionMade(self):
		self.transport.write("Welcome!\n")
		self.transport.write("COMMANDS:\n")
		self.transport.write("NICK <Nickname>\n")
		self.transport.write("MSG <Recipient> <text>\n")
		self.transport.write("BROADCAST <text>\n\n")
		self.factory.on_connection_open(self)
	def connectionLost(self, reason):
		self.factory.on_connection_close(self)
	def dataReceived(self, data):
		input = data.split(' ')
		if data.startswith("NICK"):
			if input[1]:
				self.nickname = input[1].split('\r\n')[0]
				self.factory.on_data("HELLO " + self.nickname + "!")
		elif data.startswith("BROADCAST"):
			self.factory.on_broadcast(self.nickname + " :" + data.replace("BROADCAST", ""), self.nickname)
		elif data.startswith("MSG"):
			if input[1]:
				self.factory.on_pm(self.nickname + " :" + data.replace("MSG " + input[1], ""), input[1])
		else:
			self.factory.on_data("COMMAND NOT FOUND")

class MyProtocolFactory(protocol.Factory):
	def __init__(self):
		self.users = []
	def buildProtocol(self, addr):
		return MyProtocol(self)
	def on_connection_open(self, protocol):
		print("New connection")
		self.users.append(protocol)
	def on_connection_close(self, protocol):
		print("Connection closed")
		self.users.remove(protocol)
	def on_data(self, data):
		for user in self.users:
			user.transport.write("\n" + data + "\n")
	def on_pm(self, data, usr):
		for user in self.users:
			if(user.nickname == usr):
				user.transport.write("\n" + data + "\n")
				break
	def on_broadcast(self, data, usr):
		for user in self.users:
			if(user.nickname != usr):
				user.transport.write("\n" + data + "\n")

reactor.listenTCP(8050, MyProtocolFactory())
reactor.run()