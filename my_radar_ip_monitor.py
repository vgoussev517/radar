import socket

from PyQt5.QtCore import QThread

from my_ip_service import UDP_Service_For_Radar
from radar_messages import RM_Message, RMM_Radar_Net_Address_Setup, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RMM_Track_Message, \
    RM_Target_Data


if __name__ == "__main__":
    import time

    monitor = UDP_Service_For_Radar()
    monitor.this_ip_port = ("127.0.0.2", 4006)  # is to be local address
    monitor.that_ip_port = ("127.0.0.1", 4003)
    monitor.start_service()

    i = 0
    print("Radar monitor started!")
    while True:
        msg = monitor.recv_message()
        msg.print("{0} Got message {1}".format(time.time(), i))
        i += 1
