import string
from math import sin
from random import random

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor

from agent import Agent
from my_3d_viewer import My_3D_Viewer_Widget
from point_3d import Point_3D


# class Lissajous_3D_Gen(Agent):
class Lissajous_3D_Gen:
    def __init__(self, name: string, center: Point_3D, amplitude: Point_3D, afreq: Point_3D, phase: Point_3D):
        # super().__init__(name)
        self.name = name
        self.center = center
        self.amplitude = amplitude
        self.afreq = afreq
        self.phase = phase
        self.time = 0.0
        self.position = self.next_position(0)
        self.speed = Point_3D(0.0, 0.0, 0.0)
        pass

    def next_position(self, dt: float):
        self.time = self.time + dt
        d = self.center.d + self.amplitude.d * sin(2 * 3.14 * self.afreq.d * self.time + self.phase.d)
        w = self.center.w + self.amplitude.w * sin(2 * 3.14 * self.afreq.w * self.time + self.phase.w)
        h = self.center.h + self.amplitude.h * sin(2 * 3.14 * self.afreq.h * self.time + self.phase.h)
        if dt > 0:
            self.speed = Point_3D((d-self.position.d)/dt, (w-self.position.w)/dt, (h-self.position.h)/dt)
        self.position = Point_3D(d, w, h)
        # self.position.print("next_position: ")
        return self.position

    def get_position(self):
        return self.position

    def get_speed(self):
        return self.speed


# class My_Environment(Agent):
class My_Environment:
    def __init__(self, name):
        self.scene_min = Point_3D(0, 0, 0)
        self.scene_size = Point_3D(500, 250, 250)
        self.view_scale = 1.0
        self.target_speed_factor = 1.0
        self.track_tail_length = 100
        #
        self.name = name
        self.viewer = None
        self.n_of_targets = 0
        self.targets_gens = []
        self.viewer_target_tracks = []
        pass

    def create(self):
        self.viewer = My_3D_Viewer_Widget(
            scene_min=self.scene_min, scene_size=self.scene_size, view_scale=self.view_scale
        )
        pass

    def create_random_target(
            self, name: string = None, color: QColor = None, amplitude_scale=0.5, afreq_scale=1.0
    ) -> Lissajous_3D_Gen:
        if name is None:
            target_name = "X"+str(self.n_of_targets)
        else:
            target_name = name
        if color is None:
            # c = QColor.fromHsl(int(255*random()), int(255*random()), 200)
            c = QColor.fromHsvF(random(), 0.9, 0.9)
            target_color = QColor(c)
        else:
            target_color = color
        #
        center = self.scene_min.add(self.scene_size.scale(0.50).random()).add(self.scene_size.scale(0.20))
        amplitude = self.scene_size.scale(amplitude_scale).random()
        freq = Point_3D(afreq_scale, afreq_scale, afreq_scale).random().add(Point_3D(0.01, 0.01, 0.01))
        phase = Point_3D(3.14, 3.14, 3.14).random()
        gen = Lissajous_3D_Gen(target_name+"_Gen", center, amplitude, freq, phase)
        self.targets_gens.append(gen)
        #
        track = self.viewer.add_new_track(name=target_name, color=target_color, initial_pos=gen.get_position())
        track.set_tail_len(self.track_tail_length)
        self.viewer_target_tracks.append(track)
        #
        self.n_of_targets = self.n_of_targets + 1
        return gen

    def add_target(self, name: string, color: QColor, gen: Lissajous_3D_Gen, track_tail_length=None):
        if track_tail_length is None:
            target_track_tail_length = self.track_tail_length
        else:
            target_track_tail_length = track_tail_length
        self.targets_gens.append(gen)
        track = self.viewer.add_new_track(name=name, color=color, initial_pos=gen.get_position())
        track.set_tail_len(target_track_tail_length)
        self.viewer_target_tracks.append(track)
        self.n_of_targets = self.n_of_targets + 1
        pass

    def do_step(self, dt_s):
        for i in range(0, self.n_of_targets):
            pos = self.targets_gens[i].next_position(dt_s)
            self.viewer_target_tracks[i].move_to(pos)
        pass


if __name__ == "__main__":
    import sys
    from PyQt5.QtCore import Qt, QThread
    from PyQt5.QtWidgets import QApplication
    from my_widgets import My_Main_Window

    app = QApplication(sys.argv)
    window = My_Main_Window("Main Window")
    window.show()

    env = My_Environment("Top")
    env.create()
    env.create_random_target(afreq_scale=0.1)
    env.create_random_target(afreq_scale=0.1)
    env.create_random_target(afreq_scale=0.1)

    center = env.scene_min.add(env.scene_size.mul(Point_3D(3/4, 1/2, 1/2)))
    amplitude = env.scene_size.mul(Point_3D(1/8, 1/4, -1/4))
    afreq = Point_3D(0.2, 0.4/3, 0.4)
    phase = Point_3D(3.14/4, +0.1, +0.1)
    # afreq = Point_3D(0.8/3, 0.4/3, 0.4)
    # phase = Point_3D(+3.14*1/4.0, +3.14*1/4, 3.14*3/4+0.1)
    gen_x = Lissajous_3D_Gen("Gen_x", center, amplitude, afreq, phase)
    env.add_target(name="gen_x", color=Qt.red, gen=gen_x, track_tail_length=1000)

    window.setCentralWidget(env.viewer)

    dt_ms = 50
    while True:
        env.do_step(dt_ms/1000)
        QApplication.processEvents()
        QThread.msleep(dt_ms)
        # print("BBB")

    # app.exec()
