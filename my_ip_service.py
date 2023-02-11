import logging
import socket
import time

from PyQt5.QtCore import QThread

from radar_messages import RM_Message, RMM_Radar_Net_Address_Setup, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RMM_Track_Message, \
    RM_Target_Data

logger = logging.getLogger(__name__)


def set_logger(level=logging.INFO, file_name=None, console_level=None) -> logging.Logger:
    logger.setLevel(level)
    log_formatter = logging.Formatter("%(asctime)s: %(filename)s: %(levelname)s: %(message)s")
    if file_name is not None:
        log_file_handler = logging.FileHandler(file_name, mode='w')
        log_file_handler.setLevel(level)
        log_file_handler.setFormatter(log_formatter)
        logger.addHandler(log_file_handler)
    if console_level is not None:
        log_cons_handler = logging.StreamHandler()
        log_cons_handler.setLevel(console_level)
        log_cons_handler.setFormatter(log_formatter)
        logger.addHandler(log_cons_handler)
    return logger
    pass


class UDP_Service_For_Radar(QThread):
    OFF = 0
    SERVER = 1
    CLIENT = 2
    MULTI_CLIENT_SERVER = 3
    CLIENT_FOR_MULTI_CLIENT_SERVER = 4

    def __init__(self):
        super().__init__()
        self.mode = UDP_Service_For_Radar.OFF
        self.this_ip_address = ("127.0.0.1", 4003)  # is to be local address
        self.that_ip_address = ("127.0.0.10", 4006)  #
        self.recv_buffer_size = 1024
        self.ping_timeout_sec = 5.0     # server ping and listen_for_connections() message timeout
        self.ping_period_sec = 1.0      # client ping period
        self.recv_timeout_sec = 1.0     # recv() message timeout
        # self.client_forget_count = 10   # the number of ping timeout to forget a client
        #
        self.that_ip_addresses_ = []  # to send to for multy-server mode
        self.that_ip_addresses_last_ping_time_ = []
        self.send_message_sock_ = None
        self.recv_message_sock_ = None
        self.listen_sock_ = None
        pass

    # this is bidirectional single connection server
    #   - that_ip_address is used to send messages to client
    #   - this_ip_address is used to get messages from client
    #   - both send() and get() as well as derivatives can be used
    #   - server and client use different sockets
    def start_server(self):
        self.send_message_sock_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.recv_message_sock_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.recv_message_sock_.settimeout(self.recv_timeout_sec)
        self.recv_message_sock_.bind(self.this_ip_address)
        self.mode = UDP_Service_For_Radar.SERVER
        logger.info("Server service started. Receive is bind to: {0}".format(self.this_ip_address))
        pass

    # this is bidirectional single connection client
    #   - that_ip_address is used to send messages to server
    #   - this_ip_address is used to get messages from server
    #   - both send() and get() as well as derivatives can be used
    #   - server and client use different sockets
    def start_client(self):
        self.send_message_sock_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.recv_message_sock_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.recv_message_sock_.settimeout(self.recv_timeout_sec)
        self.recv_message_sock_.bind(self.this_ip_address)
        self.mode = UDP_Service_For_Radar.CLIENT
        logger.info("Client service started. Receive is bind to: {0}".format(self.this_ip_address))
        pass

    # this is one-directional multiple connection transmitting-only server
    #   - that_ip_address and that_ip_addresses are used to send to
    #   - that_ip_addresses is field automatically by listening this_ip_address:
    #     - client may want to add its address to that_ip_addresses by sending any message to this_ip_address
    #     - client is to ping server by sending any message to this_ip_address for keeping connection
    #     - client may want to remove its address from that_ip_addresses by sending "FORGET" to this_ip_addresses
    #   - get() and derivatives are not to be used !!!
    #   - server and client use the same sockets
    def start_multi_client_server(self):
        self.send_message_sock_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.listen_sock_ = self.send_message_sock_
        self.listen_sock_.settimeout(self.ping_timeout_sec)
        self.listen_sock_.bind(self.this_ip_address)
        self.mode = UDP_Service_For_Radar.MULTI_CLIENT_SERVER
        self.run = self.listening_connections
        self.start()
        logger.info("Multy-server service started. Listening for connections: {0}".format(self.this_ip_address))
        pass

    # this is semi-one-directional single connection client for transmitting-only multi-server
    #   - that_ip_address is used both to send control to server and get messages from server
    #   - send(bytes("PING", "utf-8")) is to be only used for pinging server - now generated automaticly
    #   - send(bytes("FORGET", "utf-8")) may be used to tell server to forget this client - now generated when closed
    #   - server and client use the same sockets
    def start_client_for_multi_client_server(self):
        self.send_message_sock_ = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.recv_message_sock_ = self.send_message_sock_
        self.recv_message_sock_.settimeout(self.recv_timeout_sec)
        self.recv_message_sock_.bind(self.this_ip_address)
        # self.listen_sock_ = self.send_message_sock_
        self.mode = UDP_Service_For_Radar.CLIENT_FOR_MULTI_CLIENT_SERVER
        self.run = self.pinging_connections
        self.start()
        logger.info("Client service started. Receive is bind to: {0}".format(self.this_ip_address))
        pass

    def listening_connections(self):
        while True:
            try:
                (message, address) = self.listen_sock_.recvfrom(self.recv_buffer_size)
                this_time = time.time()
                # if address is self.that_ip_address:
                #     logger.info("Received message from the default connection {0}: {1}".format(address, message))
                if address not in self.that_ip_addresses_:
                    self.that_ip_addresses_.append(address)
                    self.that_ip_addresses_last_ping_time_.append(this_time)
                    logger.info("Registered connection from {0}: {1}".format(address, message))
                else:
                    index = self.that_ip_addresses_.index(address)
                    self.that_ip_addresses_last_ping_time_[index] = this_time
                    logger.info("Ping connection from {0}: {1}".format(address, message))
                if message == "FORGET":
                    index = self.that_ip_addresses_.index(address)
                    self.that_ip_addresses_.pop(index)
                    self.that_ip_addresses_last_ping_time_.pop(index)
                    logger.info("Forgotten client {0} by client request".format(address))
                n_of = len(self.that_ip_addresses_)
                for index in range(n_of-1, -1, -1):
                    if this_time - self.that_ip_addresses_last_ping_time_[index] > self.ping_timeout_sec:
                        logger.info("Forgotten client {0} due to no ping".format(
                            self.that_ip_addresses_[index]
                        ))
                        self.that_ip_addresses_last_ping_time_.pop()
                        self.that_ip_addresses_.pop()
                pass  # for
            except socket.timeout as msg:
                n_of = len(self.that_ip_addresses_)
                logger.info("listen_for_connections() exception: {0}".format(msg))
                logger.info("listen_for_connections(): registered connections: {0}".format(n_of))
                for index in range(n_of-1, -1, -1):
                    this_time = time.time()
                    if this_time - self.that_ip_addresses_last_ping_time_[index] > self.ping_timeout_sec:
                        logger.info("Forgotten client {0} due to no ping".format(
                            self.that_ip_addresses_[index]
                        ))
                        self.that_ip_addresses_last_ping_time_.pop()
                        self.that_ip_addresses_.pop()
                pass  # for
            pass  # try
        pass  # while

    def pinging_connections(self):
        ping_message = bytes("PING by {0}".format(self.this_ip_address), "utf-8")
        while True:
            self.send(ping_message)
            time.sleep(self.ping_period_sec)
        pass

    def close(self):
        if self.mode == UDP_Service_For_Radar.CLIENT_FOR_MULTI_CLIENT_SERVER:
            self.send(bytes("FORGET", "utf-8"))
        if self.send_message_sock_ is not None:
            self.send_message_sock_.close()
            self.send_message_sock_ = None
        if self.recv_message_sock_ is not None:
            self.recv_message_sock_.close()
            self.recv_message_sock_ = None
        if self.listen_sock_ is not None:
            self.listen_sock_.close()
            self.listen_sock_ = None
        n_of = len(self.that_ip_addresses_)
        for index in range(n_of - 1, -1, -1):
            logger.info("Forgotten client {0} due to closing".format(self.that_ip_addresses_[index]))
            self.that_ip_addresses_last_ping_time_.pop()
            self.that_ip_addresses_.pop()
        if self.isRunning():
            self.quit()
        logger.info("Closed service {0} ".format(self.mode))
        self.mode = UDP_Service_For_Radar.OFF
        pass

    def send(self, message: bytes):
        if self.mode != self.MULTI_CLIENT_SERVER:
            rc = self.send_message_sock_.sendto(message, self.that_ip_address)
            logger.debug("Sent {0} bytes to {1}".format(rc, self.that_ip_address))
        else:
            for address in self.that_ip_addresses_:
                rc = self.send_message_sock_.sendto(message, address)
                logger.debug("Sent {0} bytes to {1}".format(rc, address))
        # print("Sent {0} bytes to {1}: {2} ".format(rc, self.that_ip_port, message))
        pass

    def get(self) -> bytes:
        try:
            (message, address) = self.recv_message_sock_.recvfrom(self.recv_buffer_size)
        # except OSError as msg:
        except socket.timeout as msg:
            logger.debug("get() exception: {0} {1}".format(self.recv_message_sock_, msg))
            return bytes(0)
        logger.debug("Get {0} bytes from {1}".format(len(message), address))
        # print("Get {0} bytes from {1}: {2}".format(len(message), address, message))
        return message

    def send_message(self, message: RM_Message):
        self.send(message.pack())
        pass

    def recv_message(self) -> RM_Message:  # we think that we got single whole message in a Datagram
        byte_msg = self.get()
        byte_msg_len = len(byte_msg)
        if byte_msg_len == 0:
            return None
        start_id_field = byte_msg[0]
        type_field = byte_msg[1]
        length_field = (byte_msg[2] << 8) + byte_msg[3]
        message: RM_Message
        if start_id_field != RM_Message.START_ID:
            logger.error("ERROR: message_receiver(): Invalid  START_ID: got={0}, expected={1}".format(
                start_id_field, RM_Message.START_ID
            ))
        if length_field != byte_msg_len:
            logger.error("ERROR: message_receiver(): Invalid  Length: got={0}, length_field={1}".format(
                byte_msg_len, length_field
            ))
        if type_field == RM_Message.MT_NET_ADDR_SETUP:
            message = RMM_Radar_Net_Address_Setup(0,0,0,0,0)
            if byte_msg_len != RM_Message.MLEN_NET_ADDR_SETUP:
                logger.error("ERROR: message_receiver(): wrong RMM_Radar_Net_Address_Setup length")
        elif type_field == RM_Message.MT_NORTH_CORNER_SETUP:
            message = RMM_Radar_North_Corner_Setup(0,0,0)
            if byte_msg_len != RM_Message.MLEN_NORTH_CORNER_SETUP:
                logger.error("ERROR: message_receiver(): wrong RMM_Radar_North_Corner_Setup length")
        elif type_field == RM_Message.MT_PARAMETER_SETUP:
            message = RMM_Radar_Parameter_Setup(0,0,0,0,0)
            if byte_msg_len != RM_Message.MLEN_PARAMETER_SETUP:
                logger.error("ERROR: message_receiver(): wrong RMM_Radar_Parameter_Setup length")
        elif type_field == RM_Message.MT_TX_SWITCH_CTRL:
            message = RMM_Radar_Tx_Switch_Control(0)
            if byte_msg_len != RM_Message.MLEN_TX_SWITCH_CTRL:
                logger.error("ERROR: message_receiver(): wrong RMM_Radar_Parameter_Setup length")
        elif type_field == RM_Message.MT_NET_ADDR_STATUS:
            message = RMM_Radar_Net_Address_Status(0,0,0,0)
            if byte_msg_len != RM_Message.MLEN_NET_ADDR_STATUS:
                logger.error("ERROR: message_receiver(): wrong RMM_Radar_Net_Address_Status length")
        elif type_field == RM_Message.MT_TRACK_MESSAGE:
            n_of_targets = byte_msg[5]
            targets = [RM_Target_Data() for k in range(n_of_targets)]
            message = RMM_Track_Message(targets)
            if byte_msg_len != RM_Message.MLEN_TRACK_MESSAGE+RM_Message.MLEN_TARGET*n_of_targets:
                logger.error("ERROR: message_receiver(): wrong RMM_Radar_Net_Address_Status length")
        else:
            message = RM_Message()
            message.type_name = "Unknown type"
            pass
        message.unpack(byte_msg)
        return message
        pass

    def echo_server(self):
        buffer_size = 1024
        # bytes_to_send = str.encode(msg_from_server)
        # self.from_sock.bind(("127.0.01", 20001))
        logger.info("Echo server started")
        while True:
            (message, address) = self.recv_message_sock_.recvfrom(buffer_size)
            logger.debug("Echo server: get {0} bytes from {1}: {2}".format(len(message), address, message))
            # Sending a reply to client
            # rc = self.from_sock.sendto(message, address)
            rc = self.send_message_sock_.sendto(message, self.that_ip_address)
            logger.debug("Echo server: echoed {0} bytes to {1}: {2} ".format(rc, self.that_ip_address, message))
        pass

    def echo_client(self, msg_to_send):
        logger.info("Echo client started")
        message = str.encode(msg_to_send)
        address = self.that_ip_address
        rc = self.recv_message_sock_.sendto(message, address)
        # rc = self.to_sock.sendto(bytes_to_send, ("127.0.01", 20001))
        logger.debug("Echo client: sent {0} bytes to {1}: {2} ".format(rc, address, message))
        # (message, address) = self.to_sock.recvfrom(buffer_size)
        (message, address) = self.send_message_sock_.recvfrom(self.recv_buffer_size)
        logger.debug("Echo client: get {0} bytes from {1}: {2}".format(len(message), address, message))
        pass


if __name__ == "__main__":
    # my_ip_service_logger = logging.getLogger("my_ip_service")
    my_ip_service_logger = logging.getLogger(__name__)
    my_ip_service_logger.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s")
    logger_file_handler = logging.FileHandler(f"{__file__}.log", mode='w')
    logger_file_handler.setFormatter(logger_formatter)
    my_ip_service_logger.addHandler(logger_file_handler)
    # print(my_ip_service_logger)

    server = UDP_Service_For_Radar()
    server.this_ip_address = ("127.0.0.1", 10003)  # is to be local address
    server.that_ip_address = ("127.0.0.2", 10006)
    server.start_server()
    server.run = server.echo_server
    server.start()
    print("aaa")

    QThread.msleep(100)
    client = UDP_Service_For_Radar()
    client.this_ip_address = ("127.0.0.2", 10006)  # is to be local address
    client.that_ip_address = ("127.0.0.1", 10003)
    client.start_client()
    # client.echo_client("Hello world")
    client.send(str.encode("Hello world"))
    msg = client.get()
    print("bbb: ", msg)

    print()
    start_time = time.time()
    tracks = []
    for i in range(2):
        track = RM_Target_Data()
        track.track_lot.set(i*10+3)
        tracks.append(track)
    msg_track = RMM_Track_Message(tracks)
    msg_track.update()
    end_time = time.time()
    msg_track.print("To send: ")
    print('RMM_Track_Message create time: ', end_time-start_time)
    client.send_message(msg_track)

    msg_track_recv = client.recv_message()
    msg_track_recv.print("Received: ")
