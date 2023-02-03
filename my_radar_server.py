# Radar messages structures
import logging
import sys
from copy import deepcopy
from math import sqrt, sin, cos
from operator import mod

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication

from my_environment import My_Environment, Lissajous_3D_Gen
from my_ip_service import UDP_Service_For_Radar
from my_radar import My_Radar
from my_widgets import My_Main_Window
from point_3d import Point_3D, Point_3D_Polar

# logger = logging.getLogger(__name__)
logger = logging.getLogger("my_ip_service")
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s: %(filename)s: %(levelname)s: %(message)s")
#
log_file_handler = logging.FileHandler(f"{__file__}.log", mode='w')
log_file_handler.setLevel(logging.DEBUG)
log_file_handler.setFormatter(log_formatter)
logger.addHandler(log_file_handler)
#
log_cons_handler = logging.StreamHandler()
log_cons_handler.setLevel(logging.INFO)
log_cons_handler.setFormatter(log_formatter)
logger.addHandler(log_cons_handler)
# установка уровня логирования конкретно этого обработчика



# print(my_ip_service_logger)


#############################
if __name__ == "__main__":
    import time

    app = QApplication(sys.argv)

    env = My_Environment("Top")
    env.create()
    afreq_scale = 0.1
    env.create_random_target(afreq_scale=afreq_scale)
    env.create_random_target(afreq_scale=afreq_scale)
    env.create_random_target(afreq_scale=afreq_scale)
    center = env.scene_box.mul(Point_3D(3/4, 1/2, 1/2))
    amplitude = env.scene_box.mul(Point_3D(1/8, 1/4, -1/4))
    freq = Point_3D(1.0, 2.0/3, 2.0).scale(afreq_scale)
    phase = Point_3D(3.14/4, +0.1, +0.1)
    # freq = Point_3D(0.8/3, 0.4/3, 0.4)
    # phase = Point_3D(+3.14*1/4.0, +3.14*1/4, 3.14*3/4+0.1)
    gen_x = Lissajous_3D_Gen("Gen_x", center, amplitude, freq, phase)
    env.add_target(name="gen_x", color=Qt.red, gen=gen_x, track_tail_length=1000)
    print("Environment with targets created")

    window = My_Main_Window("Environment")
    window.show()
    window.setCentralWidget(env.viewer)
    print("Viewer created")

    radar = My_Radar()
    radar.ip_service.this_ip_port = ("127.0.0.1", 4003)  # is to be local address
    radar.ip_service.that_ip_port = ("127.0.0.2", 4006)
    radar.send_period_ms = 100
    radar.start()
    print("Radar started!")

    i = 0
    delay_ms = int(radar.send_period_ms/2)
    start_time = time.time()
    this_time = time.time()
    while True:
        # logger.info("Loop")
        last_time = this_time
        this_time = time.time()
        dt_s = this_time - last_time
        env.do_step(dt_s=dt_s)
        for k in range(0, env.n_of_targets):
            radar.add_track_point(
                track_id=k, time_s=this_time,
                position=env.targets_gens[k].get_position(),
                speed=env.targets_gens[k].get_speed()
            )
        if mod(i, 20) == 0:
            for point in radar.track_points:
                point.print("BBB")
            print()
        QApplication.processEvents()
        QThread.msleep(delay_ms)
        i += 1

