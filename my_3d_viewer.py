import string
from random import random

from PyQt5.QtCore import QSize, Qt, QRectF, QSizeF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QGroupBox, \
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, \
    QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsLineItem


class Point_3D:
    def __init__(self, d, w, h):
        self.d = d
        self.w = w
        self.h = h

    def print(self, msg=None):
        if msg is None:
            print("3d point: ({0:f}, {1:f}, {2:f})".format(self.d, self.w, self.h))
        else:
            print("{0}: ({1:f}, {2:f}, {3:f})".format(msg, self.d, self.w, self.h))

    def move_to(self, d, w, h):
        self.d = d
        self.w = w
        self.h = h

    def add(self, x):
        return Point_3D(self.d+x.d, self.w+x.w, self.h+x.h)

    def sub(self, x):
        return Point_3D(self.d-x.d, self.w-x.w, self.h-x.h)

    def mul(self, x):
        return Point_3D(self.d*x.d, self.w*x.w, self.h*x.h)

    def scale(self, x: float):
        return Point_3D(self.d*x, self.w*x, self.h*x)

    def random(self):
        return Point_3D(self.d*random(), self.w*random(), self.h*random())


class My_2D_Track_tail(QGraphicsItemGroup):
    def __init__(self, color: QColor, initial_pos_x, initial_pos_y):
        super().__init__()
        self.last_x = initial_pos_x
        self.last_y = initial_pos_y
        self.length = 100000
        self.color = color
        self.points = []
        pass

    def add_point(self, x, y):
        # print("add_point: x: {0}->{1}, y: {2}->{3}".format(self.last_x, x, self.last_y, y))
        line = QGraphicsLineItem(self.last_x, self.last_y, x, y, self)
        line.setPen(self.color)
        self.addToGroup(line)
        self.points.append(line)
        self.last_x = x
        self.last_y = y
        if len(self.points) > self.length:
            self.removeFromGroup(self.points.pop(0))
        pass

    def set_length(self, n):
        self.length = n
        while len(self.points) > self.length:
            self.removeFromGroup(self.points.pop(0))
        pass


class My_2D_Track:
    def __init__(self, name: string, color: QColor, initial_pos_x, initial_pos_y):
        super().__init__()
        self.name = name
        self.color = color
        size = 8
        text_offset_x = -0
        text_offset_y = -20
        # create track head
        self.head = QGraphicsItemGroup()
        text = QGraphicsSimpleTextItem(name)
        text.setBrush(color)
        text.setPos(text_offset_x, text_offset_y)
        self.head.addToGroup(text)
        circle = QGraphicsEllipseItem(-size/2, -size/2, size, size)
        circle.setBrush(color)
        self.head.addToGroup(circle)
        # self.setFlag(QGraphicsItem.ItemIsMovable)   # we do not want to move it with mouse!!!
        # create track tail
        self.tail = My_2D_Track_tail(QColor(color).darker(300), initial_pos_x, initial_pos_y)
        #
        self.head.setPos(initial_pos_x, initial_pos_y)
        pass

    def move_to(self, x: float, y: float):
        self.head.setPos(x, y)
        self.tail.add_point(x, y)
        pass

    def set_tail_len(self, n):
        self.tail.set_length(n)
        pass


class My_2D_Track_Graph_Widget(QGraphicsView):
    def __init__(self, scene_size_x, scene_size_y):
        super().__init__()
        self.tracks = []
        self.default_line_width = 1.0
        self.scene_margin_x = 10  # scene to view margin
        self.scene_margin_y = 10  # scene to view margin
        self.x_min = 0.0  # scene left-top coordinate
        self.y_min = 0.0  # scene left-top coordinate
        self.x_max = self.x_min + scene_size_x  # scene right-bottom coordinate
        self.y_max = self.y_min + scene_size_y  # scene right-bottom coordinate
        self.scene = QGraphicsScene(self.x_min, self.y_min, scene_size_x, scene_size_y)
        # self.scene.setSceneRect(self.x_offset, self.y_offset, self.x_max_size, self.y_max_size)
        # self.scene.setSceneRect(0, 0, 500, 250)
        self.add_axis_and_grid(x_grid=50, y_grid=50)
        self.setFixedSize(2*self.scene_margin_x+scene_size_x, 2*self.scene_margin_y+scene_size_y)
        # self.resize(QSize(self.x_max_size, self.y_max_size))
        self.setBackgroundBrush(Qt.black)
        self.setScene(self.scene)
        # self.scale(1.75, 1.75)
        # self.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # overrides self.setFixedSize()
        # print(self.scene.sceneRect())

    def add_axis_and_grid(self, x_grid, y_grid):
        # axis_pen = QPen(Qt.darkGreen, self.default_line_width, style=Qt.SolidLine)
        # self.scene.addLine(self.x_offset, self.y_offset, self.x_max_size, self.y_offset, pen=axis_pen)
        # self.scene.addLine(self.x_offset, self.y_offset, self.x_offset, self.y_max_size, pen=axis_pen)
        grid_pen = QPen(Qt.darkGreen, self.default_line_width/2, style=Qt.DotLine)
        x = self.x_min
        while x <= self.x_max:
            self.scene.addLine(x, self.y_min, x, self.y_max, pen=grid_pen)
            x = x + x_grid
        y = self.y_min
        while y <= self.y_max:
            self.scene.addLine(self.x_min, y, self.x_max, y, pen=grid_pen)
            y = y + y_grid
        pass

    def add_track(self, track_2d: My_2D_Track):
        self.tracks.append(track_2d)
        self.scene.addItem(track_2d.head)
        self.scene.addItem(track_2d.tail)
        pass

    def remove_track(self, track_2d: My_2D_Track):
        for trck in self.tracks:
            if trck == track_2d:
                self.scene.removeItem(track_2d)
                self.tracks.remove(trck)
        pass


class My_3D_Track:
    def __init__(self, name: string, color: QColor, initial_pos: Point_3D):
        self.name = name
        self.color = color
        self.pos = initial_pos
        self.track_dh = My_2D_Track(name, color, initial_pos.d, initial_pos.h)
        self.track_dw = My_2D_Track(name, color, initial_pos.d, initial_pos.w)
        self.track_wh = My_2D_Track(name, color, initial_pos.w, initial_pos.h)
        pass

    def move_to(self, pos: Point_3D):
        self.pos = pos
        self.track_dh.move_to(pos.d, pos.h)
        self.track_dw.move_to(pos.d, pos.w)
        self.track_wh.move_to(pos.w, pos.h)
        pass

    def set_tail_len(self, n):
        self.track_dh.set_tail_len(n)
        self.track_dw.set_tail_len(n)
        self.track_wh.set_tail_len(n)
        pass


class My_3D_Viewer_Widget(QWidget):
    def __init__(self, scene_box: Point_3D):
        super().__init__()
        self.scene_box = Point_3D(scene_box.d, scene_box.w, scene_box.h)
        layout = QGridLayout(self)
        widget_dh = QGroupBox("DxH")
        widget_dw = QGroupBox("DxW")
        widget_wh = QGroupBox("WxH")
        self.widget_values = QGroupBox("Values")
        layout.addWidget(widget_dh, 0, 0)
        layout.addWidget(widget_dw, 1, 0)
        layout.addWidget(widget_wh, 0, 1)
        layout.addWidget(self.widget_values, 1, 1)
        self.viewer_dh = My_2D_Track_Graph_Widget(scene_size_x=self.scene_box.d, scene_size_y=self.scene_box.h)
        self.viewer_dw = My_2D_Track_Graph_Widget(scene_size_x=self.scene_box.d, scene_size_y=self.scene_box.w)
        self.viewer_wh = My_2D_Track_Graph_Widget(scene_size_x=self.scene_box.w, scene_size_y=self.scene_box.h)
        layout_dh = QHBoxLayout(widget_dh)
        layout_dw = QHBoxLayout(widget_dw)
        layout_wh = QHBoxLayout(widget_wh)
        layout_dh.addWidget(self.viewer_dh)
        layout_dw.addWidget(self.viewer_dw)
        layout_wh.addWidget(self.viewer_wh)
        self.tracks = []
        pass

    def add_new_track(self, name: string, color: QColor, initial_pos: Point_3D):
        track_3d = My_3D_Track(name, color, initial_pos)
        self.viewer_dh.add_track(track_3d.track_dh)
        self.viewer_dw.add_track(track_3d.track_dw)
        self.viewer_wh.add_track(track_3d.track_wh)
        # track_3d.move_to(initial_pos)
        self.tracks.append(track_3d)
        return track_3d

    def add_track(self, track_3d: My_3D_Track):
        self.viewer_dh.add_track(track_3d.track_dh)
        self.viewer_dw.add_track(track_3d.track_dw)
        self.viewer_wh.add_track(track_3d.track_wh)
        # track_3d.move_to(track_3d.pos)   # just to set initial position in 2D trackers
        self.tracks.append(track_3d)
        pass

    def remove_track(self, track_3d: My_3D_Track):
        for trck in self.tracks:
            if trck == track_3d:
                self.tracks.remove(trck)
                self.viewer_dh.remove_track(trck.track_dh)
                self.viewer_dw.remove_track(trck.track_dw)
                self.viewer_wh.remove_track(trck.track_wh)
        pass


if __name__ == "__main__":
    import sys
    from my_widgets import My_Main_Window
    from PyQt5.QtCore import Qt, QThread
    from PyQt5.QtWidgets import QApplication
    from my_environment import Lissajous_3D_Gen

    app = QApplication(sys.argv)

    viewer_3d = My_3D_Viewer_Widget(Point_3D(500, 250, 250))
    # viewer_3d.show()

    window = My_Main_Window("Main Window")
    window.setCentralWidget(viewer_3d)
    window.show()

    center = Point_3D(250, 125, 125)
    amplitude = Point_3D(200, 100, 100)
    freq = Point_3D(1.0, 2.1, 4.1)
    phase = Point_3D(0.0, 0.0, 3.14/2)
    obj = Lissajous_3D_Gen("Gen", center, amplitude, freq, phase)

    track = viewer_3d.add_new_track("X1", Qt.red, obj.get_position())
    track.set_tail_len(100)
    track2 = viewer_3d.add_new_track("X2", Qt.blue, Point_3D(250, 125, 125))

    dt = 0.01
    while True:
        next_pos = obj.next_position(dt)
        # next_pos.print("At "+str(obj.time)+":")
        track.move_to(next_pos)
        # sleep(0.1)
        QThread.msleep(100)
        QApplication.processEvents()

    # graph.add_test_items()

    app.exec()
