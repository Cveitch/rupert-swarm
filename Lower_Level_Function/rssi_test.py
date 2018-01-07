"""
	Testing the Ruperts

	This is a blind rupert (address=19) shouting constantly 
	5 times a second to a base station (address=17)

	 

	Rafael Roman O.
	Feb 27, 2017
"""

import sys, traceback, time
from threading 		import Thread, BoundedSemaphore
from bridge 		import Bridge
from bridge_error 	import BridgeError

ping 		  = "ping"
my_address 	  = 19
base_station_addr = 17
running 	  = True
bridge		  = None 
uart_ticket  	  = BoundedSemaphore(1) #one thread is allowed to access the uart 
					#at any given time

def main():
	global bridge

	bridge = Bridge()	

	print( "" )	
	print( "RSSI Test" )
	print( "" )
	print( "Setting txpower=6" )
	print( "{}".format( bridge.request("write txpower 6") ) )
	print( "Setting my address to 19" )
	print( "{}".format( bridge.request( "write myaddr {}".format( my_address ) ) ) )

	#Start pinging 
	print( "Pinging base station with address {}".format( base_station_addr ) )
	print( "" )	
	
	
	t = Thread( target=ping_thread )
	t.start()
	
	#Start moving routine
	while True:

		try:
			
			#stop
			uart_ticket.acquire()
			bridge.request( "write motordir stop" )
			uart_ticket.release()
			time.sleep( 7 )

			#go forwards
			uart_ticket.acquire()
			bridge.request( "write motordir forwards" )
			uart_ticket.release()
			time.sleep( 10 )

			#stop
			uart_ticket.acquire()
			bridge.request( "write motordir stop" )
			uart_ticket.release()
			time.sleep( 7 )
			
			#go backwards
			uart_ticket.acquire()
			bridge.request( "write motordir backwards" )
			uart_ticket.release()
			time.sleep( 10 )


		except BridgeError as e:
			print( "{}".format( e.message ) )	
			running = False
			break
		except:
			traceback.print_exc()
			running = False
			break			

def ping_thread():
	"""
		Ping thread. Transmits a ping every ~100ms
	"""
	global bridge

	while running:
		try:
			uart_ticket.acquire()							# P( uart )
			bridge.request( "send {} {}".format( base_station_addr, ping )  )	# use uart
			uart_ticket.release()							# V( uart )
		except BridgeError as e:
			print( "{}".format( e.message ) )	
		except:
			traceback.print_exc()
			break

		time.sleep( 0.20 )


if __name__ == "__main__":
	main()
