#Import Dependencies
import socket

#Definitions
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = "Hello, World!"

#Report target IP, port, and msg
print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message: HI!", MESSAGE)

#Create socket
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

#Encode the string for transmission
MESSAGE = MESSAGE.encode()

#Send message
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
