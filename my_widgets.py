# coding=utf-8
# This is a sample Python script.
import string
import sys
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
        # self.setGeometry(width/8, height/8, width*0.75, height*0.75)
        # self.setFixedSize(QSize(width*0.75, height*0.75))
        self.move(width/8, height/8)

        self.area = []
        main_layout = QGridLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        for i in range(0, 4):
            # widget = QWidget()
            widget = QGroupBox(str(i))
            self.area.append(widget)
            main_layout.addWidget(widget, (i >> 1) % 2, i % 2)
        # main_layout.columnStretch(3)
        # main_layout.rowStretch(3)

        self.setCentralWidget(main_widget)
        # self.setLayout(main_layout)

    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        event.accept()
        # Thread.
        sys.exit()


class My_Track_Graph_Widget(QGraphicsView):
    def __init__(self, scene_size_x=500, scene_size_y=250):
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

    def add_test_items(self):
        # add rectangular
        rect_item = QGraphicsRectItem(QRectF(10, 10, 320, 240))
        rect_item.setBrush(Qt.red)
        # rect_item.setPen(Qt.NoPen)
        rect_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.scene.addItem(rect_item)
        # add ellipse
        ellipse_item = QGraphicsEllipseItem(QRectF(10, 10, 200, 200))
        ellipse_item.setBrush(Qt.blue)
        # ellipse_item.setPen(Qt.NoPen)
        ellipse_item.setFlag(QGraphicsItem.ItemIsMovable)
        self.scene.addItem(ellipse_item)
        # do something unknown
        # rectSizeGripItem = SizeGripItem(SimpleResizer(rect_item), rect_item)
        # ellipseSizeGripItem = SizeGripItem(SimpleResizer(ellipse_item), ellipse_item)

    def add_track(self, obj):
        # obj = MyTrackGroup(name, color)
        self.tracks.append(obj)
        self.scene.addItem(obj)
        pass


class My_Track_Object(QGraphicsItemGroup):
    def __init__(self, name: string, color: QColor):
        super().__init__()
        self.name = name
        self.color = color
        size = 8
        text_offset_x = -0
        text_offset_y = -20
        text = QGraphicsSimpleTextItem(name)
        text.setBrush(color)
        text.setPos(text_offset_x, text_offset_y)
        self.addToGroup(text)
        circle = QGraphicsEllipseItem(-size/2, -size/2, size, size)
        circle.setBrush(color)
        self.addToGroup(circle)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        pass

    def move_to(self, x: float, y: float):
        self.setPos(x, y)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = My_Main_Window("Main Window")

    graph_lh = My_Track_Graph_Widget(scene_size_x=500, scene_size_y=250)
    graph_lw = My_Track_Graph_Widget(scene_size_x=500, scene_size_y=250)
    graph_wh = My_Track_Graph_Widget(scene_size_x=250, scene_size_y=250)
    layout_lh = QHBoxLayout(window.area[0])
    layout_lw = QHBoxLayout(window.area[2])
    layout_wh = QHBoxLayout(window.area[1])
    window.area[0].setTitle("LxH")
    window.area[2].setTitle("LxW")
    window.area[1].setTitle("WxH")
    layout_lh.addWidget(graph_lh)
    layout_lw.addWidget(graph_lw)
    layout_wh.addWidget(graph_wh)

    target1 = My_Track_Object("X1", Qt.darkRed)
    graph_lh.add_track(target1)
    graph_lh.tracks[0].move_to(50, 50)

    window.show()

    layout = QHBoxLayout(window.area[3])
    layout.addWidget(QPushButton("Start"))

    # graph.add_test_items()

    app.exec()
