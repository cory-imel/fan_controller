import paho.mqtt.client as mqttClient
import time
import configparser
import RPi.GPIO as GPIO

config = configparser.ConfigParser()
config.read('config/config.txt')

MQTT_HOST = config.get('SETTINGS', 'MQTT_HOST')
MQTT_USER = config.get('SETTINGS', 'MQTT_USER')
MQTT_PASSWORD = config.get('SETTINGS', 'MQTT_PASSWORD')
MQTT_PORT = config.get('SETTINGS', 'MQTT_PORT')
MQTT_CAFILE = config.get('SETTINGS', 'MQTT_CAFILE')
MQTT_CRT = config.get('SETTINGS', 'MQTT_CRT')
MQTT_KEY = config.get('SETTINGS', 'MQTT_KEY')

GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT, initial=0)
GPIO.setup(29, GPIO.OUT, initial=0)
GPIO.setup(36, GPIO.OUT, initial=0)
GPIO.setup(37, GPIO.OUT, initial=0)
GPIO.setup(33, GPIO.OUT, initial=0)


def on_connect(client, userdata, flags, rc):
    if rc == 0:

        print("Connected to broker")

        global Connected  # Use global variable
        Connected = True  # Signal connection

    else:

        print("Connection failed")


def on_message(client, userdata, message):
    print("Message received: " + message.payload)


Connected = False  # global variable for the state of the connection


client = mqttClient.Client("Bedroom_Fan")  # create new instance
client.tls_set(ca_certs=MQTT_CAFILE, certfile=MQTT_CRT, keyfile=MQTT_KEY)
client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)  # set username and password
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback

client.connect(MQTT_HOST, port=MQTT_PORT)  # connect to broker

client.loop_start()  # start the loop

while Connected != True:  # Wait for connection
    time.sleep(0.1)

client.subscribe([("bedroom_fan/on/set", 0), ("bedroom_fan/light/set", 0)])

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()