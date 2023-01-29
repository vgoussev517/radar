import socket

from PyQt5.QtCore import QThread


class UDP_Service_For_Radar(QThread):
    def __init__(self):
        super().__init__()
        self.this_ip = "127.0.0.1"  # is to be local address
        self.this_port = 4003
        self.that_ip = "127.0.0.1"
        self.that_port = 4006
        self.from_that_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.to_that_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        pass

    def start_service(self):
        self.from_that_sock.bind((self.this_ip, self.this_port))

    def send(self, message: bytes):
        address = (self.that_ip, self.that_port)
        rc = self.to_that_sock.sendto(message, (self.that_ip, self.that_port))
        print("Sent {0} bytes to {1}: {2} ".format(rc, address, message))
        pass

    def get(self) -> bytes:
        buffer_size = 1024
        (message, address) = self.from_that_sock.recvfrom(buffer_size)
        print("Get from {0}: {1}".format(address, message))
        return message

    def echo_server(self):
        buffer_size = 1024
        # bytes_to_send = str.encode(msg_from_server)
        # self.from_sock.bind(("127.0.01", 20001))
        print("Echo server: started")
        while True:
            (message, address) = self.from_that_sock.recvfrom(buffer_size)
            print("Echo server: get from {0}: {1}".format(address, message))
            # Sending a reply to client
            # rc = self.from_sock.sendto(message, address)
            address = (self.that_ip, self.that_port)
            rc = self.to_that_sock.sendto(message, address)
            print("Echo server: echoed {0} bytes: {1} to {2}".format(rc, message, address))
        pass

    def echo_client(self, msg_to_send):
        print("Echo client: started")
        message = str.encode(msg_to_send)
        address = (self.that_ip, self.that_port)
        rc = self.to_that_sock.sendto(message, address)
        # rc = self.to_sock.sendto(bytes_to_send, ("127.0.01", 20001))
        print("Echo client: sent {0} bytes to {1}: {2} ".format(rc, address, message))
        buffer_size = 1024
        # (message, address) = self.to_sock.recvfrom(buffer_size)
        (message, address) = self.from_that_sock.recvfrom(buffer_size)
        print("Echo client: get from {0}: {1}".format(address, message))
        pass


if __name__ == "__main__":
    import time

    server = UDP_Service_For_Radar()
    server.this_ip = "127.0.0.1"  # is to be local address
    server.this_port = 4003
    server.that_ip = "127.0.0.2"
    server.that_port = 4006
    server.start_service()
    server.run = server.echo_server
    server.start()
    print("aaa")

    QThread.msleep(100)
    client = UDP_Service_For_Radar()
    client.this_ip = "127.0.0.2"  # is to be local address
    client.this_port = 4006
    client.that_ip = "127.0.0.1"
    client.that_port = 4003
    client.start_service()
    # client.echo_client("Hello world")
    client.send(str.encode("Hello world"))
    msg = client.get()
    print("bbb: ", msg)
