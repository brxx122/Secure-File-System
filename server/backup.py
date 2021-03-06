# def Login(client, address):
	# client.settimeout(500)
	# while 1:
		# try:
			# buf = client.recv(MAXBUFF)
		# except:
			# client.close()
		# if not buf or buf == "q":
			# print address, ' close the connect'
			# break
		# print 'Received:', buf, 'from', address
		# client.send(buf)
	# client.close()	
	
	
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# s.bind((HOST,PORT))		#server ip 
# s.listen(MAXCONN)

# while True:
# client, address = s.accept()
# print 'Connected by', address
# thread = threading.Thread(target=Login, args=(client, address))


#------------- client transmit----------------#
#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import os
import threading, getopt, sys, string

MAXBUFF = 2048

opts, args = getopt.getopt(sys.argv[1:], "hp:l:",["help","port=","list="])

HOST = '127.0.0.1'	#localhost
PORT = 8001
MAXCONN = 50

def usage():
	print """
    -h --help             print the help
    -l --list             Maximum number of connections
    -p --port             To monitor the port number 
	"""

for op,value in opts:
	if op in ("-l", "--list"):
		MAXCONN = string.atol(value)
	elif op in ("-p","--port"):
		PORT = string.atol(value)
	elif op in ("-h"):
		usage()
		sys.exit()

if __name__ == '__main__':
	while 1:
		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect((HOST,PORT))
			message = raw_input("input: ")
			s.sendall(message)
			if not message or message == "q":
				break
			print 'ServerOutput: ' + s.recv(MAXBUFF)
		finally:
			s.close()
	# s.close()