"""
	backend.py

	Thread safe high-level access to Feather M0's backend

	Rafael Roman O.
	Macth 3, 2017

"""
from bridge_error 	import BridgeError
from bridge 		import Bridge
from backend_error	import BackendError

class Backend:


	bridge = None
	bridge_ticket = None  #for coordinating access to bridge, provided by user of backend

	def __init__( self, bridge, bridge_ticket ):
		"""
			Initializes backend

			Note that the user of the backend provides a bridge and semaphore objects.  In this manner
			the user can circumvent backend and still make sure access is syncrhonized.
		"""
		self.bridge = bridge
		self.bridge_ticket = bridge_ticket

	def set_myaddr( self, address ):
		if self.bridge is None:
			raise BackendError( "Bridge is not initialized" )
		if self.bridge_ticket is None:
			raise BackendError( "Bridge semaphore not initialized" )  

		try:
			self.bridge_ticket.acquire()							#P(bridge)
			response = self.bridge.request( "write myaddr {}".format( address ) )		#Send over the bridge
			self.bridge_ticket.release()							#V(bridge)

			return response
		except Bridge as e:
			raise BackendError( "Failed to set address {}. Error from bridge: {}".format(address, e.message) )
		except:
			raise BackendError( "Failed to set address {}. Unknown error.".format(address) )


	def set_txpower( self, power ):
		if self.bridge is None:
			raise BackendError( "Bridge is not initialized" )
		if self.bridge_ticket is None:
			raise BackendError( "Bridge semaphore not initialized" )  

		try:
			self.bridge_ticket.acquire()							#P(bridge)
			response = self.bridge.request( "write txpower {}".format( power ) )		#Send over the bridge
			self.bridge_ticket.release()							#V(bridge)

			return response
		except Bridge as e:
			raise BackendError( "Failed to set tx power {}. Error from bridge: {}".format(power, e.message) )
		except:
			raise BackendError( "Failed to set tx power {}. Unknown error.".format(power) )



	def send_msg( self, msg, address ):
		if self.bridge is None:
			raise BackendError( "Bridge is not initialized" )
		if self.bridge_ticket is None:
			raise BackendError( "Bridge semaphore not initialized" )  

		try:
			self.bridge_ticket.acquire()							#P(bridge)
			response = self.bridge.request( "send {} {}".format( address, msg ) )		#Send over the bridge
			self.bridge_ticket.release()							#V(bridge)

			return response
		except Bridge as e:
			raise BackendError( "Failed to send message to addresse {}. Error from bridge: {}".format(address, e.message) )
		except:
			raise BackendError( "Failed to send message to addresse {}. Unknown error.".format(address) )


	def set_motordir( self, direction ):
		if self.bridge is None:
			raise BackendError( "Bridge is not initialized" )
		if self.bridge_ticket is None:
			raise BackendError( "Bridge semaphore not initialized" )  

		try:
			self.bridge_ticket.acquire()							#P(bridge)
			response = self.bridge.request( "write motordir {}".format( direction ) )	#Send over the bridge
			self.bridge_ticket.release()							#V(bridge)

			return response
		except Bridge as e:
			raise BackendError( "Failed to set direction: {}. Details: {}".format(direction, e.message) )
		except:
			raise BackendError( "Failed to set direction {}. Unknown error.".format(direction) )


