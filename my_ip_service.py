import logging
import socket

from PyQt5.QtCore import QThread

from radar_messages import RM_Message, RMM_Radar_Net_Address_Setup, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RMM_Track_Message, \
    RM_Target_Data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# print(logger)


class UDP_Service_For_Radar(QThread):
    def __init__(self):
        super().__init__()
        self.this_ip_port = ("127.0.0.1",4003)  # is to be local address
        self.that_ip_port = ("127.0.0.1", 4006)
        self.from_that_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.to_that_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        pass

    def start_service(self):
        self.from_that_sock.bind(self.this_ip_port)
        logger.info("Service started. Listening: {0}".format(self.this_ip_port))
        pass

    def send(self, message: bytes):
        rc = self.to_that_sock.sendto(message, self.that_ip_port)
        logger.debug("Sent {0} bytes to {1}".format(rc, self.that_ip_port))
        # print("Sent {0} bytes to {1}: {2} ".format(rc, self.that_ip_port, message))
        pass

    def get(self) -> bytes:
        buffer_size = 1024
        (message, address) = self.from_that_sock.recvfrom(buffer_size)
        logger.debug("Get {0} bytes from {1}".format(len(message), address))
        # print("Get {0} bytes from {1}: {2}".format(len(message), address, message))
        return message

    def send_message(self, message: RM_Message):
        self.send(message.pack())
        pass

    def recv_message(self) -> RM_Message:  # we think that we got single whole message in a Datagram
        byte_msg = self.get()
        byte_msg_len = len(byte_msg)
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
            (message, address) = self.from_that_sock.recvfrom(buffer_size)
            logger.debug("Echo server: get {0} bytes from {1}: {2}".format(len(message), address, message))
            # Sending a reply to client
            # rc = self.from_sock.sendto(message, address)
            rc = self.to_that_sock.sendto(message, self.that_ip_port)
            logger.debug("Echo server: echoed {0} bytes to {1}: {2} ".format(rc, self.that_ip_port, message))
        pass

    def echo_client(self, msg_to_send):
        logger.info("Echo client started")
        message = str.encode(msg_to_send)
        address = self.that_ip_port
        rc = self.to_that_sock.sendto(message, address)
        # rc = self.to_sock.sendto(bytes_to_send, ("127.0.01", 20001))
        logger.debug("Echo client: sent {0} bytes to {1}: {2} ".format(rc, address, message))
        buffer_size = 1024
        # (message, address) = self.to_sock.recvfrom(buffer_size)
        (message, address) = self.from_that_sock.recvfrom(buffer_size)
        logger.debug("Echo client: get {0} bytes from {1}: {2}".format(len(message), address, message))
        pass


if __name__ == "__main__":
    import time

    # my_ip_service_logger = logging.getLogger("my_ip_service")
    my_ip_service_logger = logging.getLogger(__name__)
    my_ip_service_logger.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s")
    logger_file_handler = logging.FileHandler(f"{__file__}.log", mode='w')
    logger_file_handler.setFormatter(logger_formatter)
    my_ip_service_logger.addHandler(logger_file_handler)
    # print(my_ip_service_logger)

    server = UDP_Service_For_Radar()
    server.this_ip_port = ("127.0.0.1", 4003)  # is to be local address
    server.that_ip_port = ("127.0.0.2", 4006)
    server.start_service()
    server.run = server.echo_server
    server.start()
    print("aaa")

    QThread.msleep(100)
    client = UDP_Service_For_Radar()
    client.this_ip_port = ("127.0.0.2", 4006)  # is to be local address
    client.that_ip_port = ("127.0.0.1", 4003)
    client.start_service()
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
