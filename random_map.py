# coding=utf-8
# This is a sample Python script.
import string
import sys
from random import random
from randomapi import RandomJSONRPC
from threading import Thread

from PyQt5.QtCore import QSize, Qt, QRectF, QSizeF, QThread
from PyQt5.QtGui import QColor, QColorConstants, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QHBoxLayout, QGroupBox, \
    QGraphicsSimpleTextItem
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem, QGraphicsEllipseItem, \
                            QGraphicsItemGroup


class My_Main_Window(QMainWindow):
    def __init__(self, title):
        super().__init__()
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        height = screen_rect.height()
        width = screen_rect.width()
        self.setWindowTitle(title)
        self.move(width/8, height/8)
        self.width = 500
        self.hight = 500

        self.graph = My_Graph_Widget(self.width, self.hight)
        self.setCentralWidget(self.graph)


class Mass:
    i = 0

    def __init__(self, x, y, m):
        Mass.i = Mass.i + 1
        self.indx = Mass.i
        self.name = "Mass {}".format(i)
        self.alife = True
        self.m = m
        self.x = x
        self.y = x
        self.vx = 0.0
        self.vy = 0.0
        self.ax = 0.0
        self.ay = 0.0

    def print(self):
        print("{0} {1}: m={2}, x={3}, y={4}, vx={5}, vy={6}, ax={7}, ay={8}".format(
              self.name, self.alife, self.m, self.x, self.y, self.vx, self.vy, self.ax, self.ay
              ))

    def fuse(self, obj):
        m = self.m + obj.m
        px = self.m*self.vx + obj.m*obj.vx
        py = self.m*self.vy + obj.m*obj.vy
        self.m = m
        self.vx = px/m
        self.vy = py/m
        self.name = "{0}+{1}".format(self.name, obj.indx)
        obj.alife = False


class Universe:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.default_m = 1.0
        self.masses = []
        pass

    def create(self, n):
        for i in range(0, n):
            x =
            y =
            obj =
        pass




class My_Graph_Widget(QGraphicsView):
    def __init__(self, scene_size_x=500, scene_size_y=500):
        super().__init__()
        self.default_line_width = 1.0
        self.scene_margin_x = 10  # scene to view margin
        self.scene_margin_y = 10  # scene to view margin
        self.x_min = 0.0  # scene left-top coordinate
        self.y_min = 0.0  # scene left-top coordinate
        self.x_max = self.x_min + scene_size_x  # scene right-bottom coordinate
        self.y_max = self.y_min + scene_size_y  # scene right-bottom coordinate
        self.scene = QGraphicsScene(self.x_min, self.y_min, scene_size_x, scene_size_y)
        self.setFixedSize(2*self.scene_margin_x+scene_size_x, 2*self.scene_margin_y+scene_size_y)
        self.setBackgroundBrush(Qt.black)
        self.setScene(self.scene)

    def add_point(self, x, y, m):
        grid_pen = QPen(Qt.green, self.default_line_width, style=Qt.DotLine)
        self.scene.addLine(x, y, x, y, pen=grid_pen)

        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = My_Main_Window("Main Window")
    window.show()

    api_key="7d4ea951-3450-49ce-8f6a-e4add62831f4"
    # api_key="b1138918-62f2-4c91-8f9a-2c5ebb9a8427"

    random_client = RandomJSONRPC(api_key)

    n_of_points = 500
    cycles = 0
    while cycles<10:
        cycles += 1
        points = random_client.generate_integers(n=2*n_of_points, min=0, max=window.width).parse()
        print(".", end="")
        sys.stdout.flush()
        for i in range(0, n_of_points):
            x = points[i*2]
            y = points[i*2+1]
            # x = random()*window.width
            # y = random()*window.hight
            window.graph.add_point(x, y)
            QApplication.processEvents()
            QThread.msleep(10)

    app.exec()
