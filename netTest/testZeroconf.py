import socket
hostname = "modacServer"

ipAddr = socket.gethostbyname(hostname[0:-1])
print (ipAddr)