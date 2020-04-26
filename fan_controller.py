import paho.mqtt.client as mqttClient
import time
import configparser
import RPi.GPIO as GPIO
import ssl
import logging

logging.basicConfig(filename="/var/tmp/fan_controller.log", level=logging.DEBUG,format="%(asctime)s:%(levelname)s:%(message)s")

config = configparser.ConfigParser()
config.read('/home/xoxide/config/config.txt')

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

        logging.debug("Connected to broker")

        global Connected  # Use global variable
        Connected = True  # Signal connection

    else:

        logging.debug("Connection failed")


def on_message(client, userdata, message):
    logging.debug("Received message '" + str(message.payload) + "' on topic '" + message.topic + "' with QoS " + str(message.qos))
    if str(message.topic) == "/bedroom_fan/light/set":
        GPIO.output(31, 1)
        time.sleep(0.5)
        GPIO.output(31, 0)
    elif str(message.topic) == "/bedroom_fan/speed/set":
        logging.debug(str(message.payload))
        if str(message.payload) == "off":
            GPIO.output(33, 1)
            time.sleep(0.5)
            GPIO.output(33, 0)
        elif str(message.payload) == "b'low'":
            GPIO.output(29, 1)
            time.sleep(0.5)
            GPIO.output(29, 0)
        elif str(message.payload) == "b'medium":
            GPIO.output(36, 1)
            time.sleep(0.5)
            GPIO.output(36, 0)
        elif str(message.payload) == "b'high":
            GPIO.output(37, 1)
            time.sleep(0.5)
            GPIO.output(37, 0)


Connected = False  # global variable for the state of the connection

client = mqttClient.Client("Bedroom_Fan")  # create new instance
client.tls_set(ca_certs=MQTT_CAFILE, certfile=MQTT_CRT, keyfile=MQTT_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)  # set username and password
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback

client.connect(MQTT_HOST, port=int(MQTT_PORT))  # connect to broker

client.loop_start()  # start the loop

while not Connected:  # Wait for connection
    time.sleep(0.1)

client.subscribe([("/bedroom_fan/speed/set", 0), ("/bedroom_fan/light/set", 0)])

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    logging.debug("exiting")
finally:
    client.disconnect()
    client.loop_stop()
    GPIO.cleanup() 