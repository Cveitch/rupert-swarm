"""
	Use it to test communication over the uart bridge. Run as
	
	$ sudo python3 terminal.py


	Chances are you need to setup the uart (serial0) first. Google: 

	'Configuring the GPIO Serial Port on Raspbian Jessie Including Pi 3'

	It's an article on spellfoundry.com. Follow it.

	Rafael Roman O.
	Feb 26, 2017
"""
import sys, traceback
from bridge import Bridge
from bridge_error import BridgeError

def main():
	print( "" )	
	print( "Terminal for the Feather-M0-to-Pi-Zero bridge" )
	print( "" )
	print( "Pre-requisites: ")
	print( "   - The Feather M0 must be wired to serial0 in the Pi Zero" )
	print( "   - Configure serial0 (follow link in terminal.py )" )
	print( "" )
	print( "Example use:" )
	print( "   Feather-M0 > write motordir left     <<---- Command to be interpreted by the Feather M0" )
	print( "   Motor direction set                  <<---- Feather M0's reply" )
	print( "" )
	print( "For a description of commands availables see bridge.py" ) 
	print( "" )
	print( "Ctrl+C to exit" )
	print( "" )
	
	bridge = Bridge()

	while True:
		#show prompt
		sys.stdout.write( "Feather-M0 > " )
		sys.stdout.flush()

		#read line
		line = sys.stdin.readline()
		line = line[ 0:len(line)-1 ]  #strip newline char

		#print response		
		response = ""
		try:
			print( "{}".format( bridge.request(line) ) ) 
		except BridgeError as e:
			print( "{}".format(e.message) )
		except:
			traceback.print_exc()
	
		print( "" )

if __name__ == "__main__":
	main()
