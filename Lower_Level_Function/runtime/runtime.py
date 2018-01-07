"""
	runtime.py

	The runtime is in control of the PI Zero. WHat is executed, when and how.


	Rafael Roman O.
	March 11, 2017

"""
import time, sys, traceback, os
from backend	  	 import Backend
from backend_error	 import BackendError
from bridge	  	 import Bridge
from bridge_error	 import BridgeError
from threading 	  	 import Thread, BoundedSemaphore
from importlib.machinery import SourceFileLoader

base_station_address	= 111
behaviour_fname 	= "./behaviour/behaviour.py"    # the behaviour program for this rupert
running			= True				# are we still running?
behaviour_module	= None				# for accesing behaviour.py im_alive and events
behaviour_ticket	= BoundedSemaphore(1)		# at most one thread can acess the behaviour module at any given time
							# ... actually events and im_alive are accessed concurrently, but loading
							# ... and event execution are mutually exclusive, we dont want to trigger an event when 
							# ... the module is being loaded
backend			= None
bridge			= None
bridge_ticket		= None

def main():
	global running
	global backend
	global bridge
	global bridge_ticket

	#init backend
	bridge 		= Bridge()
	bridge_ticket   = BoundedSemaphore(1) 
	backend 	= Backend( bridge, bridge_ticket )

	#Start behaviour thread
	print( "Rupert being brought to life from file: {}".format( behaviour_fname )  )
	t = Thread( target=behaviour_thread )
	t.start()
		
	#Listens for events
	print( "Listening for events" )
	event_polling()

	#Clean and exit
	running = False
	print( "Behaviour Execution finalized" )
	
def behaviour_thread():
	'''
		This thread runs the behaviour filename. Brings the Rupert
		to life, if you will. 
	'''
	global behaviour_fname
	global behaviour_module	
	global backend

	try:
		#load behaviour module
		behaviour_ticket.acquire()  #P
		behaviour_module = SourceFileLoader( "behaviour.behaviour", behaviour_fname ).load_module()
		behaviour_ticket.release()  #V		

		#run
		behaviour_module.im_alive(  backend  )
		print( "RUPERT DIE (we're very sorry)" )
	except:
		print( "UNHANDLED ERROR IN RUPERT BHEHAVIOUR. Sorry, but we're not god. " )
		print( "This is the traceback:" )
		print( "---------------------" )
		traceback.print_exc()


def event_polling():
	'''
		Polls the Feather backend for events
	'''
	global running

	while running:
	
		# -- polls for messages --
		response = poll_message()
		status 	 = response[ 'status' ]
		raw_msg  = response[ 'msg' ]

		if status == 'msg update' :
			result = parse_payload( raw_msg )
			status = result[ 'status' ]

			if status is 'empty':
				print( "WARNING: Payload of behaviour  update message was empty. Ignoring update request." )
			else:
				behaviour_file_update( result[ 'payload' ] )

		elif status == 'msg rupert':
			behaviour_event( "msg received", raw_msg  )

		elif status == 'error':
			print( "Failed to poll received messages from backend. Details: " )
			print( "" )
			print( "{}".format( raw_msg ) )
			print( "This is the traceback:" )
			print( "---------------------" )
			traceback.print_exc()
			running = False

		#polls for batt level
		#... this evetually triggers a low batt level
		#... or a battery has been plugged

		#polls for other sutff
		#...


		# -- sleep --
		time.sleep( 0.1 ) #100ms

def parse_payload( raw_msg ):
	'''
		Returns the payload of a msg
	'''
	payload_index = raw_msg.find( 'payload=' )

	if payload_index== -1:
		return { 'status' : 'empty', 'payload' : 'payload not found' }
	else:
		payload_index = payload_index + len( 'payload=' )
		payload = raw_msg[ payload_index : len(raw_msg) ]
		return { 'status' : 'payload found', 'payload' : payload }


def parse_from( raw_msg ):
	'''
		Returns the source address of a msg
	'''
	fields = raw_msg.split( ',' )

	from_content = ""
	from_index = -1
	
	#get from field and where the actual from value begins
	for field in fields:
		if "from" in field:
			from_content = field
			from_index = field.find( '=' )
			break

	if from_index== -1:
		return { 'status' : 'empty', 'from' : 'from not found' }
	else:
		from_final = from_content[ from_index+1 : len(from_content) ]
		return { 'status' : 'from found', 'from' : from_final }


def parse_rssi( raw_msg ):
	'''
		Returns the rssi of a msg
	'''
	fields = raw_msg.split( ',' )

	rssi_content = ""
	rssi_index = -1
	
	#get from field and where the actual from value begins
	for field in fields:
		if "rssi" in field:
			rssi_content = field
			rssi_index = field.find( '=' )
			break

	if rssi_index == -1:
		return { 'status' : 'empty', 'rssi' : 'rssi not found' }
	else:
		rssi = rssi_content[ rssi_index+1 : len(rssi_content) ]
		return { 'status' : 'rssi found', 'rssi' : rssi }
	
	

def behaviour_file_update( contents ):
	'''
		Replace the old behaviour file 

	'''
	global behaviour_fname
	print( "Behaviour file update received {}".format( behaviour_fname ) )

	#Kill rupert
	print( "Killing Rupert (MISSING...)" )

	#Replace behaviour file
	print( "Replacing behaviour file" )
	try:
		#os.remove( behaviour_fname )
		with open( behaviour_fname, "w" ) as f:
			f.write( contents )
	except:
		print( "Failed to replace behaviour file. Something went wrong" )
		traceback.print_exc()

	#Start behaviour thread
	print( "Rupert being brought to life from file: {}".format( behaviour_fname )  )
	t = Thread( target=behaviour_thread )
	t.start()


def behaviour_event( event, raw_msg ):
	'''
		Delivers a message to the behaviout thread running
	
	'''
	global behaviour_module

	#parse msg
	payload    = parse_payload( raw_msg )[ 'payload' ]
	from_addr  = parse_from( raw_msg )[ 'from' ]
	rssi 	   = parse_rssi( raw_msg )[ 'rssi' ] 
	
	#deliver msg
	behaviour_ticket.acquire() # P

	if behaviour_module != None :
		#Module is laoded. Execute event in this thread
		behaviour_module.event_msg_received( payload, from_addr, rssi )		
	else:
		print( "WARNING: Message ignore. Behaviour module not loaded." )

	behaviour_ticket.release() # V	


def poll_message():
	'''
		Asks the backend for any received messages and return the next in the received buffer, if any.
	'''
	
	global backend
	global base_station_address
	global bridge
	global bridge_ticket

	try:
		# poll backend for received messages
		bridge_ticket.acquire()
		response = bridge.request( "receive" )
		bridge_ticket.release()

		# read response
		if "from={}".format( base_station_address ) in response:
			#update msg from base station
			return { "status":"msg update", "msg":response  }
		elif "from" in response:
			#message from some other rupert
			return { "status":"msg rupert", "msg":response  }
		else:
			#no msg
			return { "status":"empty", "msg":"msg not found" }
			

	except BridgeError as e:
		return { "status":"error", "msg":e.message }

	except:
		return { "status":"error", "msg":"Unexpected Error" }


	


if __name__ == "__main__" :
	main()


