/*
*   Feather-M0 side of the Feather-PiZero bridge.
*   
*   It takes ascii commands from the UART and replies
*   to them. That is it.
*    
*   Feb 26, 2017
*   Rafael R.O
*/

#include <stdio.h>
#include <RHReliableDatagram.h>
#include <RH_RF69.h>
#include <SPI.h>


//Config
#define DEBUGGING         1        //TURN DEBUGING ON/OFF HERE
#define BRIDGE_BAUD_RATE  115200   //This baud rate's and bridge.py must match.


//Radio
#define MIN_TX_POWER       0  
#define MAX_TX_POWER       31
#define MAX_NUM_MESSAGES   30    //Small buffer
#define RADIO_MIN_ADDRESS  0
#define RADIO_MAX_ADDRESS  255
#define DEFAULT_ADDRESS    0    //Default address of this node (my address)

RH_RF69 driver(8, 3); // Adafruit Feather M0 with RFM95
RHReliableDatagram manager(driver, DEFAULT_ADDRESS);

typedef struct{
    uint8_t payload[RH_RF69_MAX_MESSAGE_LEN];   //Null-terminated payload
    uint8_t from;                          
    uint8_t id;
}Message;

Message msg_buffer[MAX_NUM_MESSAGES];
uint8_t msg_tail = 0, msg_head = 0;      //Keeps track of messages in message_buffer

//Motor
#define MOTOR_MIN_SPEED 0
#define MOTOR_MAX_SPEED 5

#define INA1 A0
#define INA2 A1
#define INB1 A2 
#define INB2 A3

#define MOTOR_FORWARDS     1
#define MOTOR_BACKWARDS    2
#define MOTOR_LEFT         3
#define MOTOR_RIGHT        4
#define MOTOR_STOP         5

//Battery
#define BATTERY_PIN A7
#define BATTERY_MAX_VOLTAGE (float)4.0

//Bridge
#define MAX_REQUEST_LEN     100  //This value can't ve larger than (RH_RF69_MAX_MESSAGE_LEN + strlen(send) + whatever space an address ocupies)
#define MAX_RESPONSE_VALUE  150
char start_symbol  = '+';
char end_symbol    = '-';

//LED
#define LED_PIN  13

void setup() {

  //Init pins
   pinMode( BATTERY_PIN, INPUT );
   pinMode( LED_PIN, INPUT );
  
  //Init Motor
  motor_drive( MOTOR_STOP );
  
  pinMode( INA1, OUTPUT );
  pinMode( INA2, OUTPUT );
  pinMode( INB1, OUTPUT );
  pinMode( INB2, OUTPUT );
  
   //Init serial
#ifdef DEBUGGING
   Serial.begin( 9600 );
#endif
   Serial1.begin( BRIDGE_BAUD_RATE );
  
   //Init Radio
   while( !manager.init() )
     signal_error();    
     
   while( !driver.setFrequency(915.0) )
     signal_error();    
 
   driver.setTxPower(6);

   //Init succeded   
   signal_init_sucess();
}

char c;

void loop() { 
     
    //Request from PI Zero?
     if( (c = Serial1.read()) == start_symbol ){ 
       
         //Read request
         char request[ MAX_REQUEST_LEN ];
         read_request( request, MAX_REQUEST_LEN );
       
         //Process request
         char response[ MAX_REQUEST_LEN ];
         create_response( request, response );
     
         //reply    
#ifdef DEBUGGING
         Serial.println( response );
#endif
         Serial1.println( response );
     }
     
     
     // Message available in radio?
     if (manager.available()){
         uint8_t len = RH_RF69_MAX_MESSAGE_LEN;
         uint8_t from;
         uint8_t id;
         
         //Receive
         if ( manager.recvfromAck( msg_buffer[msg_tail].payload, &len, &from, NULL, &id ) ){
             //Message was correctly acknowledged
           
             //Store if there's space        
             if( msg_tail - msg_head <  MAX_NUM_MESSAGES ){
                   msg_buffer[msg_tail].payload[len] = '\0'; //Null-terminated payload
                   msg_buffer[msg_tail].from = from;
                   msg_buffer[msg_tail].id = id;
                   
                   msg_tail++;
             }
         }   
        
    }
    
}

/*
*   Return the RSSI level as a positive integer value
*   (To get the real one, simply do (-1)*read_last_rssi()
*/
int read_last_rssi(){
  return driver.lastRssi();
}

/*
*   Return the battery level as a float value
*   Code adapted from:
*   https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/power-management
*
*/
float read_battery_level(){
  float level = analogRead( BATTERY_PIN );
  level *= 2;    // we divided by 2, so multiply back
  level *= 3.3;  // Multiply by 3.3V, our reference voltage
  level /= 1024.0; // convert to voltage
  
  return level;
}

/*
*    It processes request and create a response for it.
*
*/
void create_response( char* request, char* response ){
   #define EQUAL 0
   char param_one[MAX_REQUEST_LEN];
   char param_two[MAX_REQUEST_LEN];
   
   if( is_command( request, "read" ) ){       
       // -- read command --

      //parse params
       parse_param( request, param_one, param_two );
       
       //process and create response
       char response_value[MAX_RESPONSE_VALUE];
       
       if( strcmp( param_one, "lastrssi" ) == EQUAL )         sprintf( response, "%c%d%c", start_symbol, read_last_rssi(), end_symbol );
       else if( strcmp( param_one, "battlevel" ) == EQUAL )   sprintf( response, "%c%d%%%c", start_symbol, (int)(( read_battery_level()/BATTERY_MAX_VOLTAGE )*100.0), end_symbol );
       else if( strcmp( param_one, "maxmsglen" ) == EQUAL )   sprintf( response, "%c%d characters%c", start_symbol, RH_RF69_MAX_MESSAGE_LEN, end_symbol );
       else if( strcmp( param_one, "no param" ) == EQUAL )    sprintf( response, "%c%s%c", start_symbol, "Param missing", end_symbol );
       else                                                   sprintf( response, "%cUnknown param %s%c", start_symbol, param_one, end_symbol );
   }
   else if( is_command( request, "write" ) ){  
       // -- write command --
       
       //parse param
       parse_param( request, param_one, param_two );

       //process and create response
       char response_value[MAX_RESPONSE_VALUE];
       if( strcmp( param_one, "motorspeed" ) == EQUAL ){
            //Change motor speed
           
            //Checks if tx power is zero (since atoi returns zero for bad formatted strings)
            bool it_was_zero = false;
            if( strcmp( param_two, "0" ) == EQUAL )
              it_was_zero = true;
           
            //Parse speed
            int speed = atoi(param_two);
            
            if( strcmp( param_two, "no param" ) == EQUAL ){
               //Create missing speed response
               sprintf( response, "%c%s%c", start_symbol, "motor speed missing", end_symbol );   
               return;
            }
            else if( speed == 0 && !it_was_zero ){
               //Create invalid power response
               sprintf( response, "%c%s%c", start_symbol, "Invalid motor speed", end_symbol );   
               return;
            }
            
            //Checks speed is in range
            if( speed < MOTOR_MIN_SPEED || speed > MOTOR_MAX_SPEED ){
                //Create invalid range response
               sprintf( response, "%cMotor speed must be in range [%d,%d]%c", start_symbol, MOTOR_MIN_SPEED, MOTOR_MAX_SPEED, end_symbol );   
               return;
            }
           
           //Set speed
           //...
           
           //create response
           sprintf( response, "%c%s%c", start_symbol, "In progress...", end_symbol );
       }
       else if( strcmp( param_one, "txpower" ) == EQUAL ){
            //Checks if tx power is zero (since atoi returns zero for bad formatted strings)
            bool it_was_zero = false;
            if( strcmp( param_two, "0" ) == EQUAL )
              it_was_zero = true;
            
            //Parse power
            int power = atoi(param_two);
            
            if( strcmp( param_two, "no param" ) == EQUAL ){
               //Create missing speed response
               sprintf( response, "%c%s%c", start_symbol, "tx power missing", end_symbol );   
               return;
            }
            else if( power == 0 && !it_was_zero ){
               //Create invalid power response
               sprintf( response, "%c%s%c", start_symbol, "Invalid tx power", end_symbol );   
               return;
            }
            
            //Checks power is in range
            if( power < MIN_TX_POWER || power > MAX_TX_POWER ){
                //Create invalid range response
               sprintf( response, "%cTx power must be in range [%d,%d]%c", start_symbol, MIN_TX_POWER, MAX_TX_POWER, end_symbol );    
               return;
            }
            
            //Set power
            driver.setTxPower(power);
           
            //Create Ok response
            sprintf( response, "%cPower set to %s (can't verify it though)%c", start_symbol, param_two, end_symbol );   
       }
       else if( strcmp( param_one, "motordir" ) == EQUAL ){
            //Change motor speed
           
            if( strcmp( param_two, "forwards" ) == EQUAL ){
              motor_drive(MOTOR_FORWARDS);
              sprintf( response, "%c%s%c", start_symbol, "Motor direction set", end_symbol );   
            }
            else if( strcmp( param_two, "backwards" ) == EQUAL ){
              motor_drive(MOTOR_BACKWARDS);
              sprintf( response, "%c%s%c", start_symbol, "Motor direction set", end_symbol );   
            }
            else if( strcmp( param_two, "left" ) == EQUAL ){
              motor_drive(MOTOR_LEFT);
              sprintf( response, "%c%s%c", start_symbol, "Motor direction set", end_symbol );   
            }
            else if( strcmp( param_two, "right" ) == EQUAL ){
              motor_drive(MOTOR_RIGHT);
              sprintf( response, "%c%s%c", start_symbol, "Motor direction set", end_symbol );   
            }
            else if( strcmp( param_two, "stop" ) == EQUAL ){
              motor_drive(MOTOR_STOP);
              sprintf( response, "%c%s%c", start_symbol, "Motor direction set", end_symbol );   
            }
            else if( strcmp( param_two, "no param" ) == EQUAL ){
              sprintf( response, "%c%s%c", start_symbol, "motor direction missing", end_symbol );   
            }
            else{
              sprintf( response, "%c%s%c", start_symbol, "invalid direction", end_symbol );  
            }
              
       }
       else if( strcmp( param_one, "myaddr" ) == EQUAL ){
            //Checks if myaddr is zero (since atoi returns zero for bad formatted strings)
            bool it_was_zero = false;
            if( strcmp( param_two, "0" ) == EQUAL )
              it_was_zero = true;
            
            //Parse address
            int address = atoi(param_two);
            
            if( strcmp( param_two, "no param" ) == EQUAL ){
               //Create missing response
               sprintf( response, "%c%s%c", start_symbol, "address missing", end_symbol );   
               return;
            }
            else if( address == 0 && !it_was_zero ){
               //Create invalid response
               sprintf( response, "%c%s%c", start_symbol, "Invalid address", end_symbol );   
               return;
            }
            
            //Checks address is in range
            if( address < RADIO_MIN_ADDRESS || address > RADIO_MAX_ADDRESS ){
                //Create invalid range response
               sprintf( response, "%cAddress must be in range [%d,%d]%c", start_symbol, RADIO_MIN_ADDRESS, RADIO_MAX_ADDRESS, end_symbol );    
               return;
            }
            
            //Set address
            manager.setThisAddress( address );
            
            //Read address to verify
            uint8_t read_address = manager.thisAddress();
           
            //Create response
            if( read_address == address )
              sprintf( response, "%cAddress set to %d%c", start_symbol, read_address, end_symbol );   
            else 
              sprintf( response, "%cFailed to set address%c", start_symbol, end_symbol );
       }
       else if( strcmp( param_one, "no param" ) == EQUAL ){
           sprintf( response, "%c%s%c", start_symbol, "No param", end_symbol );
       }
       else{
           sprintf( response, "%cUnknown param %s%c", start_symbol, param_one, end_symbol );
       }
   }
   else if( is_command( request, "send" ) ){   
       // -- send command --
       
       //parse param 
       parse_param( request, param_one, param_two );
       
       //process and create response
       if( strcmp( param_one, "no param" ) == EQUAL )      sprintf( response, "%c%s%c", start_symbol, "Address missing", end_symbol );
       else if( strcmp( param_two, "no param" ) == EQUAL ) sprintf( response, "%c%s%c", start_symbol, "Message missing", end_symbol );
       else{
         
            //Checks if the address is zero (since atoi returns zero for bad formatted strings)
            bool it_was_zero = false;
            if( strcmp( param_one, "0" ) == EQUAL )
              it_was_zero = true;
            
            //Parse address
            int address = atoi(param_one);
            
            if( address == 0 && !it_was_zero ){
               //Create invalid address response
               sprintf( response, "%c%s%c", start_symbol, "Invalid address", end_symbol );   
               return;
            }
            
            //Send  message
            bool sent = manager.sendtoWait( (uint8_t*)param_two, strlen(param_two), address );
           
           //Create Ok response
           if( sent )
              sprintf( response, "%cMessage of length %d sent to addressee %d (ack received)%c", start_symbol, strlen(param_two), address, end_symbol );   
           else
              sprintf( response, "%cFailed to deliver msg (ack not received)%c", start_symbol, end_symbol );   
             
       }
       
   }
   else if( is_command( request, "receive" ) ){   
       // -- receive command --
            
       //Have we received anything?
       if( msg_tail - msg_head >  0 ){
            //COnsume msg and create response
            sprintf( response, "%cbuffer_size=%d, id=%d, from=%d, payload=%s%c", (msg_tail - msg_head), start_symbol, msg_buffer[msg_head].id, msg_buffer[msg_head].from, end_symbol );   
            
            //Remove message from buffer
            msg_head++;
       }
       else{
            //Buffer empty
            sprintf( response, "%cBuffer empty%c", start_symbol, end_symbol );   
       }
   }
   else{    
       // -- unknown command --
       sprintf( response, "%cInvalid command%c", start_symbol, end_symbol );
   }
   
}


/*
*   Parses a param from a given null-terminated string (line).
*   (I know a string is not a line!, but I've wote it like that already
*    I am not changing it)
*
*/
void parse_param( char* line, char* param_one, char* param_two ){
   char* p_line = line;
   char* p_param_one = param_one;
   char* p_param_two = param_two;
   
   //Skips until the space before the first letter in the parameter
   while( *p_line && *p_line != ' ' )
     p_line++;
     
   
   //Checks for param
   if( *p_line == '\0' || *(p_line+1) == '\0' ){
      sprintf( param_one, "no param" );
      return;
   }
   
   //Skip until the first letter in the parameter
   p_line++;
   
   //Read everything into param one, until a space or null-char is found
   while( *p_line && *p_line != ' ' )
     *p_param_one++ = *p_line++;

   //Append null char at the end of param one
   *(p_param_one) = '\0';
   
   //Checks for param two
   if( *p_line == '\0' || *(p_line+1) == '\0' || *(p_line+1) == ' ' ){
      sprintf( param_two, "no param" );
      return;
   }
   
   //Skip until the first letter in the second parameter
   p_line++;
   
   //Read everything into param two, until a space or null-char is found
   while( *p_line && *p_line != ' ' )
     *p_param_two++ = *p_line++;
   
   //Append null char at the end of param two
   *p_param_two = '\0';
}

/*
*   Determines whether a null-terminated string (line) contains
*   a given command. (Command can only appear before the first space,
*   going from left to right)
*
*   Returns true if line contains command, false otherwise.
*/
bool is_command( char* line, char* command ){
   char* p_line = line;
   char* p_command = command;
   
   while( *p_line && *p_command ){

     if( *p_line != *p_command ) 
        return false; //found a non equal character before a space
      
     if( *p_line == ' '  )
        return true; //reached space
        
      p_line++;
      p_command++;
   }
    //Can only reach here if all characters before a space are equal     
    return true;
}

/*
*  Reads data from the UART and places it in request.
*  It will read until the end_symbol found or buf_size is reached.
*
*/
void read_request( char* request, int buf_size ){
    int i = 0;             //Start with an empty buffer
    char c;
  
    //Put UART data to buffer until end_of_symbol is received
    do{        
         //Read char
         //    Ignores non-ascii, or odd characters that are 
         //    read when no char is available at rx pin. Why no use .available() ?
         //    Because it won't work. Apparently it's a bug fixed in more recent versions.
         while( (c = Serial1.read()) > 127 );
             
         //Append to request buffer
         request[ i++ ] = c;
         
     }while( c != end_symbol && i < buf_size - 1 ); 
     
     //Append null char (replaces the end symbol)
     request[ i-1 ] = '\0';
}

void motor_drive( uint8_t direction ){
  
  switch( direction ){
     case MOTOR_FORWARDS:
       digitalWrite( INA1, HIGH );
       digitalWrite( INA2, LOW ); 
       digitalWrite( INB1, LOW );
       digitalWrite( INB2, HIGH ); 
       break;
     case MOTOR_BACKWARDS: 
       digitalWrite( INA1, LOW );
       digitalWrite( INA2, HIGH ); 
       digitalWrite( INB1, HIGH );
       digitalWrite( INB2, LOW ); 
       break;
     case MOTOR_RIGHT: 
       digitalWrite( INA1, LOW );
       digitalWrite( INA2, HIGH ); 
       digitalWrite( INB1, LOW );
       digitalWrite( INB2, HIGH ); 
       break;
     case MOTOR_LEFT: 
       digitalWrite( INA1, HIGH );
       digitalWrite( INA2, LOW ); 
       digitalWrite( INB1, HIGH );
       digitalWrite( INB2, LOW ); 
       break;
     case MOTOR_STOP:
       digitalWrite( INA1, LOW );
       digitalWrite( INA2, LOW ); 
       digitalWrite( INB1, LOW );
       digitalWrite( INB2, LOW ); 
       break;
  }
  
}

/*
*    Signal init sucess bu blinking the red LED 3 times.
*/
void signal_init_sucess(){
  
    for( int i=0; i<3; i++){
      digitalWrite( LED_PIN, HIGH );
      delay(1500);
      digitalWrite( LED_PIN, LOW );
      delay(1500);
    }
}

/*
*    Signal something bad has happened by blinking 1 time the Feather Red LED
*    Intended to be called within a loop.
*/
void signal_error(){
    digitalWrite( LED_PIN, HIGH );
    delay(200);
    digitalWrite( LED_PIN, LOW );
    delay(200);
}
