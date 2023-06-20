import paho.mqtt.client as mqtt
import time
import hashlib
import json
import ssl

# Set MQTT Broker connection information
MQTT_BROKER = "192.168.0.102"
# Using 8883 port for TLS/SSL
MQTT_PORT = 1883
MQTT_CLIENT_ID = "1"
KEEPALIVE = 15
OTA_RECEIVER_CONFIRM = "ota/ConfirmUpdate"

# Application User Logon settings (Just to indicate the presence of an authenticated user with permissions to upload EDU updates)
UPDATE_REQUESTER = "administrador"
UPDATE_REQUESTER_PASS = "123456"

# Certificates path Client Server Update
CA_CERT = "/path/to/ca.crt"  # Certificate authority certificate
CLIENT_CERT = "/path/to/client.crt"  # Client (device) certificate
CLIENT_KEY = "/path/to/client.key"  # Client (device) private key

# Create a MQTTClient object
mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
# Configure TLS/SSL
mqtt_client.tls_set(ca_certs=CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY,
                    cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, KEEPALIVE)
mqtt_client.subscribe(OTA_RECEIVER_CONFIRM)

def upload_update(filepath):
    # Read the firmware file
    with open(filepath, "r") as file:
        # Read the content of the file
        file_content = file.read()

    # Convert the data to a JSON object
    softwareUpdate = json.loads(file_content)

    # Convert the JSON object to a JSON string
    update = json.dumps(softwareUpdate)

    def calculate_hash(data):
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        return hash_obj.digest()

    def log_activity(user, versionUpdate):
        current_time = time.time()
        log_file_path = "activity_log.txt"
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{current_time}: {user} published EDU software update - {versionUpdate}\n")

    # Calculate the hash of the update
    software_hash = calculate_hash(update.encode())

    # Convert the hash to a readable representation (hexadecimal)
    hash_hex = software_hash.hex()

    # Record update request in log file
    log_activity(UPDATE_REQUESTER, update)
    # Publish the software JSON
    mqtt_client.publish("ota/Update", update)
    # Publish the hash
    mqtt_client.publish("ota/Validator", hash_hex)


# You can provide the file path manually
file_path = input("Enter the file path: ")
upload_update(file_path)

# Events loop MQTT
mqtt_client.loop_forever()