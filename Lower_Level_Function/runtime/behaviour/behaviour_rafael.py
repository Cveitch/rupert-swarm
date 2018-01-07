'''

	Rupert RSSI. It prints the RSSI of every ping ereceived over the radio.	

'''

import time
from threading import Thread

backend = None
me 	= '19'	#my address
not_me  = '2'	#the other rupert's address
txpower	= 6

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
	#t = Thread( target=driving_thread )
	#t.start()	

	#Begin pinging sequence
	while True:
		#backend.send_msg( "ping", not_me )	
		time.sleep(0.2)		
		

def driving_thread():
	'''
		This thread makes rupert go around
	'''
	global backend

	#begin driving sequence
	while True:
		backend.set_motordir( "forwards" )
		time.sleep(5)
		backend.set_motordir( "stop" )
		time.sleep(3)
		backend.set_motordir( "backwards" )
		time.sleep(5)
		backend.set_motordir( "stop" )
		time.sleep(3)
		backend.set_motordir( "left")
		time.sleep(0.5)
		backend.set_motordir( "stop" )
		time.sleep(3)
		backend.set_motordir( "right" )
		time.sleep(0.5)
		backend.set_motordir( "stop" )
		time.sleep(3)
		

def event_msg_received( msg, from_addr, rssi ):
	"""
		Message received event. KEEP THIS METHOD SHORT.
		and DO NOT ACCESS THE BACKEND from here.
	"""
	

	#ping received
	print( filter( d( int( rssi ))))

def event_low_battery():
	print( "Battery is low!" )


first_entry 	= True
max_distance 	= 5
raw_prev	= 0
raw_curr	= 0
d_prev		= 0


def filter( raw_curr ):
	global first_entry
	global max_distance
	global raw_prev
	global d_prev

	if first_entry is True: 
		#base case
		d_prev = raw_curr
		raw_prev = raw_curr
		first_entry = False
		return raw_curr
		
	direction = 'not moving'
	
	#calculate slope i
	rate = abs( raw_curr - raw_prev )

	#remove spikes
	rate = min( max_distance, rate  )
	
	if raw_curr - d_prev > 0 : 
		direction = 'farther'
	elif raw_curr - d_prev < 0 :
		direction = 'closer'
	else:
		direction = 'not moving'
	
	#calculates new position i
	if direction is 'farther':
		d_curr = d_prev + rate
	elif direction is 'closer':
		d_curr = d_prev - rate
	else:
		d_curr = d_prev

	#update previous
	raw_prev = raw_curr
	d_prev = d_curr
	
	return d_curr


def d( rssi ):
	return -rssi

