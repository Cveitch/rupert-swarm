'''

	Rupert RSSI. It prints the RSSI of every ping ereceived over the radio.	

'''

import time
from threading import Thread

backend = None
me 	= '1'	#my address
not_me  = '0'	#the other rupert's address
txpower	= 9
rssi_received = 40 # initial value for rssi - safe bet it's something like this.

def im_alive( backend_ ):
	'''
		Life begins here...
	'''
	global backend
	print( "I'm alive!" )

	#Save runtime instance
	backend = backend_

	#Init Rupert
	print( backend.set_myaddr( me ) )
	print( backend.set_txpower( txpower ) )

	#Start motor thread
	t = Thread( target=driving_thread )
	t.start()	

	#Begin pinging sequence
	while True:
		backend.send_msg( "ping", not_me )	
		time.sleep(0.2)		
		

def driving_thread():
	'''
		This thread makes rupert go around
	'''
	global backend

	#begin driving sequence
	while True:
		print( rssi )
		backend.set_motordir( "forwards" )
		time.sleep(1)
		avoid_collision()
		
		
def avoid_collision():
	'''
		Avoids colisions with other ruperts
	'''	
	global backend
	global rssi_received
	if rssi_received < 30 or rssi_received > 60:
		backend.set_motordir( "right" )
		time.sleep(0.75)


def event_msg_received( msg, from_addr, rssi ):
	"""
		Message received event. KEEP THIS METHOD SHORT.
		and DO NOT ACCESS THE BACKEND from here.
	"""
	#ping received
	global rssi_received
	rssi_received = rssi
	


def event_low_battery():
	print( "Battery is low!" )

