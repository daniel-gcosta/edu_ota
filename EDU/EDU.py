import ubinascii
import json
from umqtt.simple import MQTTClient
import machine
import network
import hashlib
import time
import os
import ujson
import _thread

# Set the WLAN network connection information
WLAN_SSID = "TESTE"
WLAN_PASS = "teste12345"

# Connect to a WLAN
connect_wlan = network.WLAN(network.STA_IF)
connect_wlan.active(True)
connect_wlan.connect(WLAN_SSID, WLAN_PASS)

while not connect_wlan.isconnected():
    pass

print('Conectado à Rede Wi-Fi')
print('Endereco IP:', connect_wlan.ifconfig()[0])
print('Mascara de Rede:', connect_wlan.ifconfig()[1])



# Set MQTT broker connection information
MQTT_BROKER = "192.168.0.102"
# Using 8883 port for TLS/SSL
MQTT_PORT = 1883
KEEPALIVE = 15

# Set MQTT topic information
OTA_TOPIC = "ota/Update"
OTA_TOPIC_HASH = "ota/Validator"
OTA_TOPIC_CONFIRM = "ota/ConfirmUpdate"

# Certificates path Client EDU
CA_CERT = "/path/to/ca.crt"  # Certificate authority certificate
CLIENT_CERT = "/path/to/client.crt"  # Client (device) certificate
CLIENT_KEY = "/path/to/client.key"  # Client (device) private key

# Set the MQTT client ID
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode("utf-8")

# Create a MQTTClient object
mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
# Configure TLS/SSL
mqtt_client.tls_set(ca_certs=CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY,
                    cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, KEEPALIVE)

# Function to load and execute files from device memory
def execute_swap():
    max_version = 0
    latest_swap = None

    # Search the device memory for the highest version number
    for filename in os.listdir():
        if filename.startswith("swap_v") and filename.endswith(".json"):
            try:
                version = int(filename.split("_v")[1].split(".json")[0])
                if version > max_version:
                    max_version = version
                    latest_swap = filename
            except:
                pass

    # Run the file with the latest version present in the device's memory
    if latest_swap:
        with open(latest_swap) as file:
            swap_data = ujson.load(file)
            code = ujson.loads(swap_data["code"])
            exec(code["code"])


# Function to calculate the hash of the update dataset
def calculate_hash(data):
    hash_obj = hashlib.sha256()
    hash_obj.update(data)
    return hash_obj.digest()


#Function to write JSON file in device memory (similar to swap)
def update_swap(content):
    # Get the next software version number (versioning)
    next_version = get_next_version()
    filename = "swap_v{}.json".format(next_version)

    # Retrieve JSON content and save to device memory
    swap_data = {
        "code": content
    }
    with open(filename, "w") as file:
        ujson.dump(swap_data, file)

    # Restarts the device for operation from the new parameters present in the update
    machine.reset()


# Function to get the number of the next version of the software file present in the device's memory
def get_next_version():
    # Check existing software files in device memory for highest version number
    max_version = 0
    for filename in os.listdir():
        if filename.startswith("swap_v") and filename.endswith(".json"):
            try:
                version = int(filename.split("_v")[1].split(".json")[0])
                max_version = max(max_version, version)
            except:
                pass

    # Increment the highest update version number to get the next version
    next_version = max_version + 1
    return next_version

# Global Variables
received_hash = None
validator_hex = None
update = None

# Callback function to process incoming messages
def mqtt_callback(topic, msg):
    global received_hash, validator_hex, update

    # Checks if the message received through the Broker has an ota/Update ID to store its content in the global variable (update)
    if topic.decode() == OTA_TOPIC:
        update = msg.decode()

        # Calculate the hash of the update
        validator = calculate_hash(update)

        # Convert the hash to a readable representation (hexadecimal)
        validator_hex = validator.hex()
    # Checks if the message received through the MQTT Broker has an ota/Validator ID to store its content in the global variable (received_hash)
    elif topic.decode() == OTA_TOPIC_HASH:
        received_hash = msg.decode()

        # Compare the received hash with the calculated hash
        if received_hash == validator_hex:
            # Write the new content to device memory
            update_swap(update)

        else:
            mqtt_client.publish(OTA_TOPIC_CONFIRM,
                                "EDU ID: " + MQTT_CLIENT_ID + " APPLICATION INTEGRITY CHECK FAILED. ABORTING UPDATE.")


# Connect to the MQTT broker and subscribe to the OTA_TOPIC and OTA_TOPIC_HASH topics
mqtt_client.connect()
mqtt_client.set_callback(mqtt_callback)
mqtt_client.subscribe(OTA_TOPIC)
mqtt_client.subscribe(OTA_TOPIC_HASH)


# Function with loop to check for updates
def check_msg_execution():
    try:
        while True:
            mqtt_client.check_msg()
            time.sleep(1)
    except Exception as e:
        print("Erro na função check_msg_execution:", str(e))

# Create a new thread to run the code
_thread.start_new_thread(check_msg_execution, ())


# Function to start execution in thread
def start_execution():
    execute_swap()
    time.sleep(1)

# Create a new thread to run the code
_thread.start_new_thread(start_execution, ())
