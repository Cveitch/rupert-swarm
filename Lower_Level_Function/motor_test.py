"""
	Testing the Ruperts

	Rafael Roman O.
	Feb 27, 2017
"""
import sys, traceback, time
from bridge import Bridge
from bridge_error import BridgeError

def main():
	print( "" )	
	print( "Testing Ruperts" )
	print( "" )
	
	bridge = Bridge()


	try:
		print( "{}".format( bridge.request("write motordir forwards") ) ) 
		time.sleep(3)
	
		print( "{}".format( bridge.request("write motordir left") ) ) 
		time.sleep(1)

		print( "{}".format( bridge.request("write motordir right") ) ) 
		time.sleep(1)

		print( "{}".format( bridge.request("write motordir forwards") ) ) 
		time.sleep(3)
			
		print( "{}".format( bridge.request("write motordir stop") ) ) 
		time.sleep(2)

		print( "{}".format( bridge.request("write motordir backwards")  ))
		time.sleep(5)
		
		print( "{}".format( bridge.request("write motordir stop") ) ) 


	except BridgeError as e:
		print( "{}".format( e.message) )	
	except:
		#stop motors
		print( "{}".format( bridge.request("write motordir stop") ) ) 		

		traceback.print_exc()
		

if __name__ == "__main__":
	main()
