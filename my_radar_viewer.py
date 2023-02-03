import socket
import sys
from random import random

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from my_3d_viewer import My_3D_Viewer_Widget
from my_ip_service import UDP_Service_For_Radar
from my_widgets import My_Main_Window
from point_3d import Point_3D, Point_3D_Polar
from radar_messages import RM_Message, RMM_Radar_Net_Address_Setup, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RMM_Track_Message, \
    RM_Target_Data


if __name__ == "__main__":
    import time

    monitor = UDP_Service_For_Radar()
    monitor.this_ip_port = ("127.0.0.2", 4006)  # is to be local address
    monitor.that_ip_port = ("127.0.0.1", 4003)
    monitor.start_service()

    app = QApplication(sys.argv)
    window = My_Main_Window("Office")
    viewer_3d = My_3D_Viewer_Widget(Point_3D(500, 250, 250))
    window.setCentralWidget(viewer_3d)
    window.show()

    i = 0
    viewer_tracks_dict = {}
    print("Radar viewer started!")
    while True:
        QApplication.processEvents()
        msg_ = monitor.recv_message()
        # msg.print("{0} Got message {1}".format(time.time(), i))

        if msg_.type.value != RM_Message.MT_TRACK_MESSAGE:
            print("ERROR: got message of wrong type")
            msg_.print("")
            continue

        msg: RMM_Track_Message = msg_
        if msg.n_of_targets.value == 0:
            print("WARNING: got message of no targets")
            msg_.print("")
            continue

        print("{0} Got message of {1} targets".format(time.time(), msg.n_of_targets.value))
        target: RM_Target_Data
        for target in msg.targets:
            target.print("")
            target_id = target.track_lot.value
            r = target.distance.value
            a = target.azimuth.value/18000*3.14159
            e = (target.zenith_angle.value-9000)/18000*3.14159
            target_pos_polar = Point_3D_Polar(r, a, e)
            target_pos_polar.print("eee")
            target_pos = target_pos_polar.return_point_3d()
            target_pos.print("eee")
            if target_id not in viewer_tracks_dict:
                target_color = QColor(QColor.fromHsvF(random(), 0.9, 0.9))
                viewer_track = viewer_3d.add_new_track("X"+str(target_id), target_color, target_pos)
                viewer_track.set_tail_len(100)
                viewer_tracks_dict[target_id] = viewer_track
            else:
                viewer_tracks_dict[target_id].move_to(target_pos)

        pass  # for
        i += 1
    pass  # while
