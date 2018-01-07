"""
	When something goes wrong in the Bridge class

	Rafael R.O
	Feb 26, 2017
"""
class BridgeError(Exception):

	def __init__( self, message ):
		super( BridgeError, self ).__init__( message )
		self.message = message
		
