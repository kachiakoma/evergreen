import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import os, random, threading, ast
from flask import json

# GPIO Pin Numbers
A_READ  = 23
A_WRITE = 24

# Climate data file
climate_file = "/climate.txt"
rgb_data = "rgb_data.txt"
MESSAGE = []
MESSAGE_0 = {'temperature': 0, 'pressure': 0, 'humidity': 0, 'windSpeed': 0,
'lux': 0, 'timestamp': 0}
MESSAGE.append(MESSAGE_0)

class Control(object):
    """Control Module"""
    GPIO.setwarnings(False)
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(A_READ, GPIO.IN)
        GPIO.setup(A_WRITE, GPIO.OUT)
        self._lock = threading.Lock()

    def read_sensorA(self):
        with self._lock:
            return GPIO.input(A_READ)

    def write_deviceA(self, value):
        with self._lock:
            GPIO.output(A_WRITE, value)

class Climate(object):
    """Get Climate Data"""
    def __init__(self):
        self._lock = threading.Lock()

    def simulate(self):
        climate_data = []
        climate_write = []
        climate_write.append(round(random.uniform(24.1, 24.9),1))
        climate_write.append(round(random.uniform(77.1, 77.9),1))
        climate_write.append(round(random.uniform(10.1, 10.9),1))
        climate_write.append(round(random.uniform(1.1, 1.6),1))

        write_file = open(climate_file, 'w')
        write_file.close()

        with self._lock:
            with open(climate_file, 'a') as file:
                for value in climate_write:
                    file.write("{}\n".format(value))
            with open(climate_file) as file:
                for line in file:
                    line.strip()
                    binary = float(line)
                    climate_data.append(binary)
        return climate_data

class Light(object):
    def rgb(self, state):
        keys = ""
        for value in state:
            keys = "{}, {}".format(keys, value)
        keys = keys[2:]
        with open(rgb_data, 'w') as file:
            file.write(keys)

class WriteOut(object):
    def __init__(self):
        self._lock = threading.Lock()

    def writeJSON(self, path, fileName, data):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        writePath = os.path.join(SITE_ROOT, path, fileName)
        with self._lock:
            text = open(writePath, 'w')
            text.write(json.dumps(data))
            text.close()
            print("Written")
            #print(data)
            """with open(writePath, 'w') as file:
                print(data)
                file.write(json.dumps(data))
                #json.dump(data, file)"""

class Mqtt_ServerA(object):
    """MQTT Client Module"""
    def on_connect(mosq, obj, flags, rc):
        print("Connected to MQTT server.")
       #print ("on_connect:: Connected with result code "+ str ( rc ) )
       #print("rc: " + str(rc))

    def on_message(mosq, obj, msg):
        """data_file = open(sensor_data, 'a')
        message = str(msg.payload.decode("utf-8"))
        data_file.write("{}\n".format(message))
        data_file.close()"""
        message = str(msg.payload.decode("utf-8"))
        message = ast.literal_eval(message)
        MESSAGE.append(message)
        #print(MESSAGE)
        #print ("on_message:: this means I got a message from broker for this topic")
        #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        #return str(msg.payload.decode("utf-8"))

    def on_publish(mosq, obj, mid):
        mid = mid
        #print("mid: " + str(mid))

    def on_subscribe(mosq, obj, mid, granted_qos):
        print("Broker has acknowledged subscribe request.")
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(mosq, obj, level, string):
        print(string)

    def on_disconnect(mosq, userdata, rc):
        if rc != 0:
            print "Unexpected MQTT disconnection. Will auto-connect"

    # Initialization of MQTT client object
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.username_pw_set("ovnwdayk", "Wb7WXP1ogA1h")
    client.connect('m11.cloudmqtt.com', 18519, 60)
    client.loop_start()
    client.subscribe('sensorData', 1)
