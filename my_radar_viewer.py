import socket
import sys
from random import random

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from agent import Agent
from my_3d_viewer import My_3D_Viewer_Widget
from my_ip_service import UDP_Service_For_Radar
from my_widgets import My_Main_Window
from point_3d import Point_3D, Point_3D_Polar
from radar_messages import RM_Message, RMM_Radar_Net_Address_Setup, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RMM_Track_Message, \
    RM_Target_Data


class My_Radar_Viewer(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.ip_client = UDP_Service_For_Radar()
        # self.ip_client.this_ip_address = ("127.0.0.2", 4006)  # should be local address but ...
        self.ip_client.this_ip_address = ("127.0.0.7", 4007)  #
        self.ip_client.that_ip_address = ("127.0.0.1", 4003)
        self.ip_client.recv_timeout_sec = 2.0
        self.ip_client.ping_period_sec = 2.5
        #
        self.viewer_3d = My_3D_Viewer_Widget(Point_3D(500, 250, 250))
        self.window = My_Main_Window("Office")
        self.window.setCentralWidget(self.viewer_3d)
        #
        self.viewer_tracks_dict = {}

    def run(self):
        self.ip_client.start_client_for_multi_client_server()
        self.window.on_close = self.close
        self.window.show()
        #
        i = 0
        self.msg("Radar viewer started!")
        while True:
            QApplication.processEvents()
            msg = self.ip_client.recv_message()
            if msg is None:
                self.msg("Receive message timeout")
                # self.monitor.send(bytes("PING", "utf-8"))
                continue
            # msg("{0} Got message {1}".format(time.time(), i))
            if msg.type.value != RM_Message.MT_TRACK_MESSAGE:
                self.err("got message of wrong type")
                msg.print("")
                continue
            #
            self.process_track_message(msg)
            pass  # for
            i += 1
        pass  # while

    def close(self):
        self.msg("Stopping Radar viewer")
        self.ip_client.close()
        self.msg("Radar viewer stopped!")
        pass

    def process_track_message(self, msg: RMM_Track_Message):
        if msg.n_of_targets.value == 0:
            self.warn("WARNING: got message of no targets")
            msg.print("")
            return
        # self.msg("Got message of {0} targets".format(msg.n_of_targets.value))
        target: RM_Target_Data
        for target in msg.targets:
            # target.print("")
            target_id = target.track_lot.value
            r = target.distance.value
            a = target.azimuth.value/18000*3.14159
            e = (target.zenith_angle.value-9000)/18000*3.14159
            target_pos_polar = Point_3D_Polar(r, a, e)
            target_pos = target_pos_polar.return_point_3d()
            if target_id not in self.viewer_tracks_dict:
                target_color = QColor(QColor.fromHsvF(random(), 0.9, 0.9))
                viewer_track = self.viewer_3d.add_new_track("X"+str(target_id), target_color, target_pos)
                viewer_track.set_tail_len(100)
                self.viewer_tracks_dict[target_id] = viewer_track
            else:
                self.viewer_tracks_dict[target_id].move_to(target_pos)
        pass


if __name__ == "__main__":
    import time
    import my_ip_service
    import logging
    logger = my_ip_service.set_logger(level=logging.DEBUG, file_name=f"{__file__}.log", console_level=logging.DEBUG)
    logger.setLevel(logging.INFO)

    app = QApplication(sys.argv)
    viewer = My_Radar_Viewer("Radar_Viewer")
    viewer.run()
    viewer.close()
    sys.exit()


