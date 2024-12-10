import socket

# Define the server address and port
server_address = ('192.168.6.11', 40100)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Send data to the server
    message = 'This is the message. It will be repeated.'
    print(f'Sending: {message}')
    sent = sock.sendto(bytes(message, "utf-8"), server_address)

    # Receive response from the server (optional)
    print('Sent...' + str(sent) + " bytes")
    #data, server = sock.recvfrom(4096)
    #print(f'Received: {message.decode()}')

finally:
    print('Closing socket')
    sock.close()