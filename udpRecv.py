#Dependencies
import socket

#Definitions
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

#Create socket
sock = socket.socket(   socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

#Bind socket (listen)
sock.bind((UDP_IP, UDP_PORT))

#Listen forever
while True:

    #Collect received data
    data, addr = sock.recvfrom(1024)
    print("received message:", data)