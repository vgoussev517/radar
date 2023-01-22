import string
from math import sin
from random import random
# from threading import Thread, Event
# from time import sleep

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor

from agent import Agent
from my_3d_viewer import Point_3D, My_3D_Viewer_Widget


# class Lissajous_3D_Gen(Agent):
class Lissajous_3D_Gen:
    def __init__(self, name: string, center: Point_3D, amplitude: Point_3D, freq: Point_3D, phase: Point_3D):
        # super().__init__(name)
        self.name = name
        self.center = center
        self.amplitude = amplitude
        self.freq = freq
        self.phase = phase
        self.time = 0.0
        self.position = self.next_position(0)
        self.speed = Point_3D(0.0, 0.0, 0.0)
        pass

    def next_position(self, dt: float):
        self.time = self.time + dt
        d = self.center.d + self.amplitude.d * sin(2 * 3.14 * self.freq.d * self.time + self.phase.d)
        w = self.center.w + self.amplitude.w * sin(2 * 3.14 * self.freq.w * self.time + self.phase.w)
        h = self.center.h + self.amplitude.h * sin(2 * 3.14 * self.freq.h * self.time + self.phase.h)
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
class My_Environment(QThread):
    def __init__(self, name, parent=None):
        # super().__init__(name)
        super().__init__(parent)
        self.name = name
        self.scene_box = Point_3D(500, 250, 250)
        self.viewer = My_3D_Viewer_Widget(self.scene_box)
        self.dt = 0.05
        self.track_tail_length = 100
        self.targets = 0
        self.targets_gens = []
        self.targets_tracks = []
        pass

    def run(self):
        while True:
            for i in range(0, self.targets):
                pos = self.targets_gens[i].next_position(self.dt)
                self.targets_tracks[i].move_to(pos)
            self.msleep(int(self.dt*1000))
            QApplication.processEvents()
            # print("BBB")
        # self.do_stop.wait()
        pass

    def create_random_target(self, name: string = None, color: QColor = None) -> Lissajous_3D_Gen:
        if name is None:
            target_name = "X"+str(self.targets)
        else:
            target_name = name
        if color is None:
            # c = QColor.fromHsl(int(255*random()), int(255*random()), 200)
            c = QColor.fromHsvF(random(), 0.9, 0.9)
            target_color = QColor(c)
        else:
            target_color = color
        #
        center = self.scene_box.scale(0.20).add(self.scene_box.scale(0.50).random())
        amplitude = self.scene_box.scale(0.50).random()
        freq = Point_3D(0.2, 0.2, 0.2).random().add(Point_3D(0.01, 0.01, 0.01))
        phase = Point_3D(3.14, 3.14, 3.14).random()
        gen = Lissajous_3D_Gen(target_name+"_Gen", center, amplitude, freq, phase)
        self.targets_gens.append(gen)
        #
        track = self.viewer.add_new_track(target_name, target_color, gen.get_position())
        track.set_tail_len(self.track_tail_length)
        self.targets_tracks.append(track)
        #
        self.targets = self.targets + 1
        return gen


if __name__ == "__main__":
    import sys
    from PyQt5.QtCore import Qt, QThread
    from PyQt5.QtWidgets import QApplication, QHBoxLayout
    from my_widgets import My_Main_Window, My_Track_Graph_Widget, My_Track_Object

    app = QApplication(sys.argv)
    window = My_Main_Window("Main Window")
    window.show()

    env = My_Environment("Top")
    env.create_random_target()
    env.create_random_target()
    env.create_random_target()

    window.setCentralWidget(env.viewer)

    # radar.start()
    env.run()
    print("AAA")

    app.exec()
