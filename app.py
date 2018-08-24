import paho.mqtt.client as mqtt, os
import paho.mqtt.publish as publish
from urlparse import urlparse
#from urllib.parse import urlparse
import time, sys, datetime
import json
import BME280_read as BME
import adafruit_mcp3008 as readadc
import RPi.GPIO as GPIO
import DefConStatus as dcs
import error as msgGen
import bmetest as test
#from yeaboi import lux
#import currentTime as stamp


# Define event callbacks
# Passes the parameters for the setting up websocket communications
# Please reference documentation in Client.py source for referencing \
# these passed parameters among the values rc will give upon connection
def on_connect(mosq, obj, flags, rc):
   print ("on_connect:: Connected with result code "+ str ( rc ) )
   print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    print ("on_message:: this means I got a message from broker for this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    if ( msg.payload == "on" ): #user must be subscribed specifically to '/sensor' topic passing message 'on' for LED ON
#    	print("Lights on")
    	GPIO.output(17,GPIO.HIGH)
    else :
#    	print("Lights off")
    	GPIO.output(17,GPIO.LOW) # any other message sent from user subscribed to topic will turn LED OFF


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

# subscribed request allow access to broker for communications from user to RPI
# user must have specific credentials from cloudmqtt.com upon
def on_subscribe(mosq, obj, mid, granted_qos):
    print("This means broker has acknowledged my subscribe request")
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

def on_disconnect(mosq, userdata, rc):
    if str(rc) != 0:
       print "Unexpected MQTT disconnection. Will auto-connect"
       print("now attempting reconnect")
       try:
           client.reconnect()
           while str(rc) !=0:
                rc = client.reconnect()
                print str(rc)
                if(str(rc) == 0):
                    break
       except:
           client.disconnect()
           print "Unsuccessful attempts. Now disconnection"

#These assignments set the function between directories from the paho/mqtt funtions from Client.py for declaration
#Please reference documentation given in the Client.py folder to understand how these functions are set up
client = mqtt.Client() #function call from mqtt directory using Client.py source assign for client call
# Assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_disconnect = on_disconnect

# Uncomment to enable debug messages
client.on_log = on_log


# user name has to be called before connect - my notes.
client.username_pw_set("ovnwdayk", "Wb7WXP1ogA1h") # These are credentials are given after creating an Instance through cloudMQTT
# Cute cat plan is free and you can find these credentials in the DETALS tab

client.connect('m11.cloudmqtt.com', 18519, 60) # (Server, Port, Timeout)

# Continue the network loop, exit when an error occurs
#rc = 0
#while rc == 0:
#    rc = client.loop()
#    client.subscribe( '/led', 2)
#    print("rc: " + str(rc))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()

vari = 0            # Declares the variance variable and sets as zero, passed to DefConStatus to
                    # change sampling frequency
PC = 0              # Percentage change variable, used to determine if variance should change
hold = 1            # Wait time variable, set from DefConStatus return, imported as dcs
LRV = [70] * 10     # Last Recorded value array, set to what value we care about. In this case, temp
i = 0               # Index for the array

#client.loop_start()
#stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# sensor_data variable is a dictionary to handle the given parameters obtained from the
# BME280(humidity,pressure,temperature) among collecting analog sensor values digitized from Anemometer
# The timestamp is collected from an NTP time server among assigning sensor pi the value of 1 for reference
sensor_data = {'temperature': 0, 'humidity': 0, 'pressure': 0, 'windSpeed': 0, 'timestamp': 0,'id':0}
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()     # should only run at the end of the program, de-references GPIOs
GPIO.setwarnings(False) #ignore GPIO flags set
GPIO.setup(17,GPIO.OUT) #Uses GPIO 17 to give user interaction over internet for toggling LED state ON/OFF

client.loop_start() # This function call loop_start() will create a threaded process to run the Client.py code
# loop_start() will handle all of the reconnection if an internet connection is lost
# all of the published/subscribed messages will be placed into a queue until the websocket realizes 0 bytes have
# been transferred resulting in a broken pipe err #32
# The thread can run around 20 minutes without internet connectivity until breaking
# If an internet access is reestablished within that given time frame, the messages queued will
# be published to the broker (try for yourself, you'll appreciate it!)

# For more user control over the network loops, please refer to documentation with using client.loop instead

windSpeed = readadc.wind_speed() # windSpeed stores the value from module readadc function wind_speed returned
temperature = BME.current_ftemp() # temperature  stores the value from module BME function current_ftemp
pressure = BME.current_pressure() # pressure stores the value from module BME function current_pressure
humidity = BME.current_humidity() # humidity store the value from module BME function current_humidity
windSpeed = round(windSpeed, 2) # round to 2 decimals
humidity = round(humidity, 2)
temperature = round(temperature, 2)
pressure = round(pressure, 3)
sensor_data['id'] = 1 # assign the value of 1 to dictionary parameter sensor_data['id']
count = 0
#rc = 0
'''while rc == 0:
    rc = client.loop()
'''
run = True
while run: # this while loop processes the real time data values obtained to be published to the broker

#    ts = time.time()
#    stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    stamp = test.now()
    windSpeed = readadc.wind_speed()
    temperature = BME.current_ftemp()
    pressure = BME.current_pressure()
    humidity = BME.current_humidity()
    windSpeed = round(windSpeed, 2)
    humidity = round(humidity, 2)
    temperature = round(temperature, 2)
    pressure = round(pressure, 3)
    sensor_data['temperature'] = temperature
    sensor_data['humidity'] = humidity
    sensor_data['pressure'] = pressure
    sensor_data['windSpeed'] = windSpeed
    sensor_data['timestamp'] = stamp
    #sensor_data['lux'] = lux
    client.subscribe ('/sensor' , 0)

    # dummy data for testing error message handling
    if(count%3 == 0):
        temperature = 30.0
        sensor_data['temperature'] = temperature
    elif(count%4 == 0):
        temperature = 110.0
        sensor_data['temperature'] = temperature

    # these conditions will check for error message handling
    # These paramters are made up for the general purpose of testing for if a
    # sensor detects something out of range, to log these errors to the webserver pi
    # please consult the agriculture department for values to be implemented within the system
    if(sensor_data['temperature'] < 50):
        client.publish('err', json.dumps(msgGen.temp_flag(temperature),1)) # temp_flag handles error message to be sent passing temperature parameter
    if(sensor_data['temperature'] > 90):
        client.publish('err', json.dumps(msgGen.temp_flag(temperature),1))
    if(windSpeed == 0):
        client.publish('err', json.dumps(msgGen.wind_flag(),1))


   # client.publish ( 'temp', BME.current_ftemp())
   # client.publish('pressure', BME.current_pressure())
   # client.publish('humidity', BME.current_humidity())
   # client.subscribe( '/led', 2)
    client.publish('sensorData', json.dumps(sensor_data),1) # uses the publish function to topic 'sensorData' to dump sensor_data as a json object
   # for publishing multiple messages within a topic
   # for general publishing/subscribing client.publish('topic', data or string, quality of service(QoS == 0,1,2)
   #                                    client.subscribe('/topic', data, QoS)

    # Calculate Percentage Change (PC) between the last 10 values and the current (initalized to 70F)
    PC = (abs((sum(LRV)/len(LRV)) - temperature) / temperature)
    # Variable frequency sampling based on percentage change between 0.5-0.01%, depending on hold time
    # 0.01 - 0.001%, depending on hold time. Increased wait time for lesser variation
    if PC < (hold * 0.00083898):  # coefficient of hold calculation is the slope of min sampling at
        vari = 1                  # 2sec/0.01% error and max sampling at 120sec/0.001% error
    elif PC > (hold * 0.00083898):
        vari = 2
    else:
        vari = 0                  # if PC doesn't change do nothing

    hold = dcs.DefCon(vari) #send vari to DefConStatus and return hold time
    LRV[i] = temperature    # Last Result Variable - set to temperature
    i = i + 1               # Increment array index
    if i > 9:               # Check if the index passed the size
        i = 0               # If it did, set it back to the beginning

    time.sleep(2)
    count += 1
