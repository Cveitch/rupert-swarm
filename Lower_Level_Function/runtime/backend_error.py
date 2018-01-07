"""
	When something goes wrong in the Backend class

	Rafael R.O
	March 3, 2017
"""
class BackendError(Exception):

	def __init__( self, message ):
		super( BackendError, self ).__init__( message )
		self.message = message
		
