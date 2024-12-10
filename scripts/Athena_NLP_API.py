# Date: 12-9-2024 
# Version: 1.0
# Description: This script sends a user input to an NLP API and forwards the response to a target endpoint.

import urllib.request
import json
import ssl
import os
import requests  # Make sure to import requests
import socket

def allow_self_signed_https(allowed):
    # Bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and \
       getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

# Allow self-signed HTTPS certificates
allow_self_signed_https(True)

# Define the API key and URL
api_key = 'cjPoKQLacyDYnyn2AzedUYZmYqDYZkG6'
url = 'https://project-sentinel-2-ekfbn.eastus2.inference.ml.azure.com/score'  # Replace with your actual endpoint URL

if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# Prepare the data
data = {
    "user_input": "Sensor 1, go to -109.5 lat, 42 long"
}

body = json.dumps(data).encode('utf-8')

# Define the headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + api_key,
    'azureml-model-deployment': 'project-sentinel-2-ekfbn-1'  # Include if needed
}

# Print the URL for debugging
print("Request URL:", url)

# Create the request
req = urllib.request.Request(url, data=body, headers=headers)
# Send the request to the API
response = urllib.request.urlopen(req)
result = response.read().decode('utf-8')
#print("API Response:", result)

# Extract final_cotString from the API response
response_json = json.loads(result)
final_cotString = response_json.get("final_cotString")

#Print to terminal
print(final_cotString)
target_ip = "192.168.100.4"
target_port = "40100"

# UDP SEND

# Define the server address and port
server_address = ('192.168.100.4', 40100)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Send data to the server
    message = 'This is the message. It will be repeated.'
    print(f'Sending: {final_cotString}')
    sent = sock.sendto(final_cotString.encode(), server_address)

    # Receive response from the server (optional)
 #   print('Waiting for a response...')
 #   data, server = sock.recvfrom(4096)
 #   print(f'Received: {data.decode()}')

finally:
    print('Closing socket')
    sock.close()

"""
target_url = f"http://{target_ip}:{target_port}/endpoint"

# Send the final_cotString as raw text to the target URL
response = requests.post(
    target_url,
    data=final_cotString.encode('utf-8'),
    headers={"Content-Type": "text/plain; charset=utf-8"},
    verify=False  # Disable SSL verification for local testing
)
print("Sent final_cotString to target:", response.text)
"""
