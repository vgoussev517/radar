import socket
import sys
import time
from operator import mod

from PyQt5.QtCore import QThread

from my_ip_service import UDP_Service_For_Radar
from radar_messages import RM_Message, RMM_Radar_Net_Address_Setup, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RMM_Track_Message, \
    RM_Target_Data


if __name__ == "__main__":
    monitor = UDP_Service_For_Radar()
    monitor.this_ip_address = ("127.0.0.6", 4006)  # is to be local address
    monitor.that_ip_address = ("127.0.0.1", 4003)
    monitor.ping_period_sec = 2.5
    monitor.recv_timeout_sec = 2.0
    monitor.start_client_for_multi_client_server()

    i = 0
    print("Radar monitor started!")
    while True:
        msg = monitor.recv_message()
        i += 1
        print(".", end="")
        sys.stdout.flush()
        if msg is None:
            print("\nrecv_message() timeout")
            # monitor.send(bytes("PING by monitor", "utf-8"))
            continue
        if mod(i, 20) == 0:
            print()
            msg.print("{0} Got message {1}".format(time.time(), i))
            pass


