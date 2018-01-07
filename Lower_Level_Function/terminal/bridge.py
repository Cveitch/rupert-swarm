"""
	bridge.py

	Bridge objects serve as bridge between the Feather-M0+ and 
	the Pi Zero. In particular, they enable the pi zero to send
	requests, and receive answers for those requests. Actual
	communication occurs via UART at 115200 bps.
	
	The Bridge class is very low-level, and concurrent access 
	to bridge objects is not supported. Do not access one or more 
	bridge objects from more than one thread or process. 
	(Sequential access to multiple objects is OK, though. As long
	 as those objects exist within the same program)


	Use example:

		bridge = Bridge()

		try:

			response = bridge.request( "read last-rssi" )	

		except BridgeError as e:
			print( "Failed to read rssi: {}".format(e.err) )



	Available requests:

		-read 	lastrssi			#reads the rssi of the last message recevied
		-read 	battlevel			#reads the battery level
		-read 	maxmsglen			#reads the maximum message length that can be sent using 'send'
		-write 	motordir   <direction>		#sets the motors' direction
		-write 	motorspeed <speed>		#sets the motors' speed
		-write 	txpower    <power>		#sets the radio's tx power
		-write  myaddr     <address>		#sets the radio's address 
		-send 	<dest address> <message> 	#sends a message  (NO SPACES IN MESSAGE)
		-receive 				#gets a recevied messgae from the message queue


		where:
			<dest address>: the addresse node's address. Adrdess must be in [0,255]
			<speed>: 	a value in the range [0,5]
			<message>:	a text message contaning only ascii characters, and NO SPACES.
			<power>:	a value in the range [0,31]  
			<direction>:	a value in { left, right, forwards, backwards, stop }

	Hardware Setup:
		Simply wire Zero's Tx to Feather's Rx, and Zero's Rx to 
		Feather's Tx. See http://pinout.xyz/pinout/uart for more details

	Rafael Roman O.
	Feb 25, 2017

"""
import wiringpi, time, sys
from bridge_error import BridgeError


class Bridge:

	uart 		= None
	init 		= False
	baudrate	= 0
	serial_device   = "/dev/serial0" 	#serial0 must be pointing to ttyAMA0. Check with ls -l /dev 
	baudrate	= 115200		#speed in bps
	start_symbol	= "+" 			#symbol used to indicate the beginning of a request/reply
	end_symbol	= "-"			#symbol used to indicate the end of a request/reply


	def __init__( self ):
		"""
			Initializes the bridge
		"""
		if self.init is False :		
			wiringpi.wiringPiSetup()
			self.__init_uart()
			self.init 	= True		

	def request ( self, request ):
		"""
			Sends a request over the bridge. 

			This function is implemented as synchronous IO. Meaning, 
			once a request has been sent, execution will halt until
			a response is received
		
		"""
		#Send request
		self.__puts( "{}{}{}".format( self.start_symbol, request, self.end_symbol ) ) 

		#Read response
		response = ""
		try:

			self.__ignore_until_start_symbol()	
			response = self.__read_until_end_symbol()

		except ValueError:	
			self.__init_uart() 
			raise BridgeError( "Bridge was reestarted due to lost connection over {} at {} bps".format( self.serial_device, self.baudrate ) )
		
		return response

		
	def __init_uart( self ):
		"""
			Inits the UART. Returns a wirinpi uart id
		"""
		self.uart = wiringpi.serialOpen( self.serial_device, self.baudrate )
		wiringpi.serialFlush( self.uart )


	def __puts( self, s ):
		"""
			Writes a string to the UART
		"""
		wiringpi.serialPuts( self.uart, s )
	
	def __getchar( self ):
		"""
			Reads a character from UART
		"""
		return  chr( wiringpi.serialGetchar( self.uart ) )

	def __ignore_until_start_symbol( self ):
		"""
			Drops everything received over the serial device,
			until it find a start symbol. Note the start symbol itself
			will be lost.
		"""
		c = ""
		while c is not self.start_symbol:
			c = self.__getchar()

	def __read_until_end_symbol( self ):
		"""
			Returns evrything read over the UART before,
			and not including, the end symbol
		"""
		response = ""
		c = " "
		while c is not self.end_symbol:
			c = self.__getchar()
			if c is not self.end_symbol: 
				response = response + c
		return response
	
			
	def close ( self ):
		"""
			Closes the UART
		"""
		if init is True:
			wiringpi.serialClose( self.uart )	
