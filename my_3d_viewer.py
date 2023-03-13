import string

from PyQt5.QtCore import QSize, Qt, QRectF, QSizeF, QRect, QPointF
from PyQt5.QtGui import QPen, QColor, QBrush, QTransform, QWheelEvent, QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent, \
    QMouseEvent
from PyQt5.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QGroupBox, \
    QGraphicsView, QGraphicsScene, QGraphicsItemGroup, \
    QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsLineItem, QPushButton, QGraphicsRectItem

from point_3d import Point_3D


class My_2D_Track_head(QGraphicsItemGroup):
    def __init__(self, name: string, color: QColor, initial_pos: QPointF):
        super().__init__()
        head_size = 6
        text_size = 16
        text_offset = QPointF(-0, -20)
        circle = QGraphicsEllipseItem(-head_size/2, -head_size/2, head_size, head_size)
        circle.setBrush(color)
        self.addToGroup(circle)
        text = QGraphicsSimpleTextItem(name)
        text.setBrush(QColor(color).darker(120))
        text.setPos(text_offset)
        self.addToGroup(text)
        self.setPos(initial_pos)
        # self.setScale(1.0)
        pass

    def rescale(self, scale: float):
        self.setScale(1.0/scale)
        pass


class My_2D_Track_tail(QGraphicsItemGroup):
    def __init__(self, color: QColor, initial_pos: QPointF):
        super().__init__()
        self.last_pos = initial_pos
        self.default_width = 1.0
        self.color = color
        self.pen = QPen(self.color, self.default_width, style=Qt.SolidLine)
        self.length = 100000
        self.points = []
        pass

    def add_point(self, pos: QPointF):
        # print("add_point: x: {0}->{1}, y: {2}->{3}".format(self.last_x, x, self.last_y, y))
        line = QGraphicsLineItem(self.last_pos.x(), self.last_pos.y(), pos.x(), pos.y(), self)
        # line.setPen(self.color)
        line.setPen(self.pen)
        self.addToGroup(line)
        self.points.append(line)
        self.last_pos = pos
        # print("add_point: len[points]={0}, length={1}".format(len(self.points), self.length))
        while len(self.points) > self.length:
            point = self.points.pop(0)
            self.removeFromGroup(point)
            self.scene().removeItem(point)  # it should be removed from the scene as well
        pass

    def set_length(self, n: int):
        self.length = n
        while len(self.points) > self.length:
            point = self.points.pop(0)
            self.removeFromGroup(point)
            self.scene().removeItem(point)  # it should be removed from the scene as well
        pass

    def rescale(self, scale: float):
        self.pen = QPen(self.color, self.default_width/scale, style=Qt.SolidLine)
        for point in self.points:  # .childItems():
            point.setPen(self.pen)
        pass


class My_2D_Track(QGraphicsItemGroup):
    def __init__(self, name: string, color: QColor, initial_pos: QPointF):
        super().__init__()
        self.name = name
        self.color = color
        self.head = My_2D_Track_head(name, color, initial_pos)
        self.tail = My_2D_Track_tail(QColor(color).darker(300), initial_pos)
        self.addToGroup(self.head)
        self.addToGroup(self.tail)
        # self.setFlag(QGraphicsItem.ItemIsMovable)   # we do not want to move it with mouse!!!
        pass

    def move_to(self, pos: QPointF):
        self.head.setPos(pos)
        self.tail.add_point(pos)
        pass

    def set_tail_len(self, n: int):
        self.tail.set_length(n)
        pass

    def rescale(self, scale: float):
        self.head.rescale(scale)
        self.tail.rescale(scale)
        pass


class My_2D_Box_n_Grid(QGraphicsItemGroup):
    def __init__(self, view):
        super().__init__()
        self.default_line_width = 1.0
        self.color = Qt.darkGreen
        # box
        box_pen = QPen(self.color, self.default_line_width, style=Qt.SolidLine)
        box_brush = QBrush(Qt.black, style=Qt.NoBrush)
        box_bounds = QRectF(view.scene_min_2d, view.scene_size_2d)
        self.box = QGraphicsRectItem(box_bounds)
        self.box.setPen(box_pen)
        self.box.setBrush(box_brush)
        self.addToGroup(self.box)
        # greed
        self.grid = QGraphicsItemGroup()
        grid_pen = QPen(self.color, self.default_line_width/2, style=Qt.DotLine)
        x = view.scene_min_2d.x()
        while x <= view.scene_max_2d.x():
            line = QGraphicsLineItem(x, view.scene_min_2d.y(), x, view.scene_max_2d.y())
            line.setPen(grid_pen)
            self.grid.addToGroup(line)
            x = x + view.scene_grid_2d.width()
        y = view.scene_min_2d.y()
        while y <= view.scene_max_2d.y():
            line = QGraphicsLineItem(view.scene_min_2d.x(), y, view.scene_max_2d.x(), y)
            line.setPen(grid_pen)
            self.grid.addToGroup(line)
            y = y + view.scene_grid_2d.height()
        self.addToGroup(self.grid)
        pass

    def rescale(self, scale: float):
        box_pen = QPen(self.color, self.default_line_width/scale, style=Qt.SolidLine)
        self.box.setPen(box_pen)
        grid_pen = QPen(self.color, self.default_line_width/2/scale, style=Qt.DotLine)
        for line in self.grid.childItems():
            line.setPen(grid_pen)
        pass


class My_2D_Track_Graph_Widget(QGraphicsView):
    def __init__(self, name, scene_x_min, scene_y_min, scene_x_size, scene_y_size, view_scale):
        super().__init__()
        self.name = name
        self.tracks = []
        self.scene_min_2d = QPointF(scene_x_min, scene_y_min)  # scene left-top coordinate
        self.scene_size_2d = QSizeF(scene_x_size, scene_y_size)
        scene_size_2dp = QPointF(scene_x_size, scene_y_size)
        self.scene_center_2d = self.scene_min_2d + scene_size_2dp/2
        self.scene_max_2d = self.scene_min_2d + scene_size_2dp
        self.scene_grid_2d = self.scene_size_2d/10
        self.view_size_2d = self.scene_size_2d*view_scale
        self.view_scale = view_scale
        self.zoom = 1.0
        self.scene_origin_2d = QPointF(0, 0)
        # scene & view
        scene = QGraphicsScene(QRectF(self.scene_min_2d, self.scene_size_2d))
        self.setScene(scene)
        view_margin_2d = QSizeF(10, 10)  # scene to view margin (black)
        view_margin_size_2d = 2 * view_margin_2d + self.view_size_2d
        self.setFixedSize(int(view_margin_size_2d.width()), int(view_margin_size_2d.height()))  # black margin
        # self.setViewportMargins(view_margin_x, view_margin_y, view_margin_x, view_margin_y)  # grey margin
        # self.setGeometry(0, 0, 2*view_margin_x+self.view_x_size, 2*view_margin_y+self.view_y_size)
        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)  # this works only  if scroll bars are enabled
        # self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setBackgroundBrush(Qt.black)
        # self.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # overrides self.setFixedSize()
        # box & grid
        self.box_and_grid = self.create_box_and_grid()
        # turn off scrollbars for Translate being working first
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().disconnect()
        self.verticalScrollBar().disconnect()
        # fit the scene and the view
        scale = self.view_scale * self.zoom
        transform_matrix = QTransform.fromScale(scale, scale)
        # translate_matrix = QTransform.fromTranslate(50, -20)
        self.setTransform(transform_matrix, combine=False)
        # self.set_zoom(self.zoom)
        self.mouse_press_pos = None
        pass

    def create_box_and_grid(self):
        box_and_grid = My_2D_Box_n_Grid(view=self)
        scale = self.view_scale * self.zoom
        box_and_grid.rescale(scale)
        self.scene().addItem(box_and_grid)
        return box_and_grid

    def add_track(self, track_2d: My_2D_Track):
        scale = self.view_scale * self.zoom
        track_2d.rescale(scale)
        self.tracks.append(track_2d)
        self.scene().addItem(track_2d)
        pass

    def remove_track(self, track_2d: My_2D_Track):
        if track_2d in self.tracks:
            self.tracks.remove(track_2d)
            self.scene().removeItem(track_2d)
        pass

    def set_zoom(self, zoom: float):
        old_scale = self.view_scale * self.zoom
        new_scale = self.view_scale * zoom
        self.zoom = zoom
        # scale view
        transform_matrix = self.transform()
        scale_x = new_scale / transform_matrix.m11()
        scale_y = new_scale / transform_matrix.m22()
        self.scale(scale_x, scale_y)
        # trim scene Rect
        old_scene_rect = self.sceneRect()
        scene_center = old_scene_rect.center()
        dist = (scene_center-self.scene_min_2d)*((1-old_scale/new_scale)*new_scale)
        self.scene_origin_2d = self.scene_origin_2d + dist
        new_scene_corner = self.scene_min_2d + self.scene_origin_2d/new_scale
        new_scene_size = self.view_size_2d/new_scale
        new_scene_rect = QRectF(new_scene_corner, new_scene_size)
        self.setSceneRect(new_scene_rect)
        # rescale items
        self.box_and_grid.rescale(new_scale)
        for track in self.tracks:
            track.rescale(new_scale)
        # print("set_zoom: zoom={0:.2f}, scale={1:.4f}, orig={2}, rect={3}".format(
        #     zoom, new_scale, self.scene_origin_2d, self.sceneRect())
        # )
        pass

    def set_scene_origin(self, x: float, y: float):
        self.scene_origin_2d = QPointF(x, y)
        scale = self.view_scale * self.zoom
        scene_rect = self.sceneRect()
        new_scene_corner = self.scene_min_2d + self.scene_origin_2d/scale
        scene_rect.moveTo(new_scene_corner)
        self.setSceneRect(scene_rect)
        # print("set_scene_origin: origin={0}, rect={1}".format(self.scene_origin_2d, self.sceneRect()))
        pass

    def set_scene_origin2(self, origin_x: float, origin_y: float):
        self.scene_x_origin = origin_x
        self.scene_x_origin = origin_y
        scale = self.view_scale * self.zoom
        m11 = scale
        m12 = 0.0
        m13 = 0.0
        m21 = 0.0
        m22 = scale
        m23 = 0.0
        m31 = origin_x
        m32 = origin_y
        dx = origin_x
        dy = origin_y
        m33 = 1
        # transform_matrix = QTransform(m11, m12, m13, m21, m22, m23, m31, m32, m33)
        transform_matrix = QTransform(m11, m12, m21, m22, dx, dy)
        self.setTransform(transform_matrix)
        # self.horizontalScrollBar().setValue(int(origin_x))
        # self.verticalScrollBar().setValue(int(origin_y))
        # print("scroolbar x={0}, y={1}".format(self.horizontalScrollBar().value(), self.verticalScrollBar().value()))
        m = self.transform()
        print("transform matrix: scx={0:.3f}, n12={1:.3f}, m13={2:.3f}, m21={3:.3f}, scy={4:.3f}, m23={5:.3f}, \
              dx={6:.3f}, dy={7:.3f}, m33={8:.3f}".
              format(m.m11(), m.m12(), m.m13(), m.m21(), m.m22(), m.m23(), m.m31(), m.m32(), m.m33())
        )
        pass

    def wheelEvent(self, e: QWheelEvent):
        # print("{0} wheel event: angleDelta={1}, phase={2}, pixelDelta={3}, x={4:.2f}, y={5:.2f}".format(
        #     self.name, e.angleDelta().y(), e.phase(), e.pixelDelta().y(), e.position().x(), e.position().y())
        # )
        if e.angleDelta().y() > 0:
            self.hook_zoom(viewer_id=self.name, dz=+1)
        elif e.angleDelta().y() < 0:
            self.hook_zoom(viewer_id=self.name, dz=-1)
        pass

    def mousePressEvent(self, e: QMouseEvent):
        # print("{0} mousePressEvent: button={1}, buttons={2}, x={3:.2f}, y={4:.2f}".format(
        #     self.name, e.button(), e.buttons(), e.pos().x(), e.pos().y())
        # )
        if e.button() == Qt.MouseButton.LeftButton:
            self.mouse_press_pos = e.pos()
            # print("MouseButton.LeftButton pressed at {0}".format(self.mouse_press_pos))
        if e.button() == Qt.MouseButton.RightButton:
            self.hook_center(viewer_id=self.name)
        pass

    def mouseMoveEvent(self, e: QMouseEvent):
        # print("{0} mouseMoveEvent: button={1}, buttons={2}, x={3:.2f}, y={4:.2f}".format(
        #     self.name, e.button(), e.buttons(), e.pos().x(), e.pos().y())
        # )
        pass
        if e.buttons() == Qt.MouseButtons(Qt.LeftButton):
            mouse_pos = e.pos()
            distance = mouse_pos - self.mouse_press_pos
            self.mouse_press_pos = mouse_pos
            # x = self.scene_x_origin - distance.x()
            # y = self.scene_y_origin - distance.y()
            self.hook_transfer(viewer_id=self.name, dx=distance.x(), dy=distance.y())
        pass

    def hook_zoom(self, viewer_id, dz):
        print("hook_zoom:  New zoom {0} by {1}".format(dz, viewer_id))
        pass

    def hook_transfer(self, viewer_id, dx, dy):
        print("hook_transfer:  transfer by dx={0}, dy={1} by {2}".format(dx, dy, viewer_id))
        pass

    def hook_center(self, viewer_id):
        print("hook_center: by {0}".format(viewer_id))
        pass


class My_3D_Track:
    def __init__(self, name: string, color: QColor, initial_pos: Point_3D):
        self.name = name
        self.color = color
        self.pos = initial_pos
        self.track_dh = My_2D_Track(name, color, QPointF(initial_pos.d, initial_pos.h))
        self.track_dw = My_2D_Track(name, color, QPointF(initial_pos.d, initial_pos.w))
        self.track_wh = My_2D_Track(name, color, QPointF(initial_pos.w, initial_pos.h))
        pass

    def move_to(self, pos: Point_3D):
        self.pos = pos
        self.track_dh.move_to(QPointF(pos.d, pos.h))
        self.track_dw.move_to(QPointF(pos.d, pos.w))
        self.track_wh.move_to(QPointF(pos.w, pos.h))
        pass

    def set_tail_len(self, n: int):
        self.track_dh.set_tail_len(n)
        self.track_dw.set_tail_len(n)
        self.track_wh.set_tail_len(n)
        pass


class My_3D_Control_Widget(QWidget):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.zoom_step = 1.25
        self.zoom_max = 5
        self.zoom_min = 0.5
        self.move_step = 50
        self.mouse_press_pos = None
        layout = QGridLayout(self)
        self.button_zoom_in = QPushButton("Zoom In")
        self.button_zoom_out = QPushButton("Zoom Out")
        self.button_up = QPushButton("Up")
        self.button_down = QPushButton("Down")
        self.button_right = QPushButton("Right")
        self.button_left = QPushButton("Left")
        self.button_to = QPushButton("To")
        self.button_away = QPushButton("Away")
        self.button_center = QPushButton("Center")
        layout.addWidget(self.button_zoom_in, 0, 0)
        layout.addWidget(self.button_zoom_out, 2, 2)
        layout.addWidget(self.button_up, 0, 1)
        layout.addWidget(self.button_down, 2, 1)
        layout.addWidget(self.button_right, 1, 2)
        layout.addWidget(self.button_left, 1, 0)
        layout.addWidget(self.button_to, 2, 0)
        layout.addWidget(self.button_away, 0, 2)
        layout.addWidget(self.button_center, 1, 1)

        self.button_zoom_in.clicked.connect(lambda: self.zoom(self.zoom_step))
        self.button_zoom_out.clicked.connect(lambda: self.zoom(1/self.zoom_step))
        self.button_center.clicked.connect(lambda: self.center())
        self.button_up.clicked.connect(lambda: self.transfer(Point_3D(0, 0, self.move_step)))
        self.button_down.clicked.connect(lambda: self.transfer(Point_3D(0, 0, -self.move_step)))
        self.button_right.clicked.connect(lambda: self.transfer(Point_3D(0, self.move_step, 0)))
        self.button_left.clicked.connect(lambda: self.transfer(Point_3D(0, -self.move_step, 0)))
        self.button_to.clicked.connect(lambda: self.transfer(Point_3D(self.move_step, 0, 0)))
        self.button_away.clicked.connect(lambda: self.transfer(Point_3D(-self.move_step, 0, 0)))
        pass

    def zoom(self, z: float):
        zoom = self.viewer.zoom*z
        if zoom < self.zoom_min or zoom > self.zoom_max:
            return
        self.viewer.set_zoom(zoom)
        print("Zoom to", zoom)
        pass

    def center(self):
        self.viewer.set_zoom(1.0)
        self.viewer.set_scene_origin(Point_3D(0, 0, 0))
        print("Center")
        pass

    def transfer(self, displacement: Point_3D):
        scene_origin = self.viewer.scene_origin.add(displacement)
        self.viewer.set_scene_origin(scene_origin)
        print("Transfer to {0}, {1}, {2}".format(scene_origin.d, scene_origin.w, scene_origin.h))
        pass

    def callback_zoom(self, viewer_id, dz):
        print("callback_zoom by {0}: dz={1}".format(viewer_id, dz))
        if dz > 0:
            self.zoom(self.zoom_step)
        elif dz < 0:
            self.zoom(1/self.zoom_step)
        pass

    def callback_transfer(self, viewer_id, dx, dy):
        print("callback_transfer by {0}: dx={1}, dy={2}".format(viewer_id, dx, dy))
        if viewer_id == "DH View":
            self.transfer(Point_3D(-dx, 0, -dy))
        elif viewer_id == "DW View":
            self.transfer(Point_3D(-dx, -dy, 0))
        elif viewer_id == "WH View":
            self.transfer(Point_3D(0, -dx, -dy))
        pass

    def callback_center(self, viewer_id):
        print("callback_center by {0}".format(viewer_id))
        self.center()
        pass


class My_3D_Viewer_Widget(QWidget):
    def __init__(self, scene_min: Point_3D, scene_size: Point_3D, view_scale: float):
        super().__init__()
        self.scene_min = scene_min
        self.scene_size = scene_size
        self.view_scale = view_scale
        self.zoom = 1.0
        self.scene_origin = Point_3D(0, 0, 0)
        layout = QGridLayout(self)
        box_widget_dh = QGroupBox("DxH")
        box_widget_dw = QGroupBox("DxW")
        box_widget_wh = QGroupBox("WxH")
        box_widget_control = QGroupBox("Control")
        layout.addWidget(box_widget_dh, 0, 0)
        layout.addWidget(box_widget_dw, 1, 0)
        layout.addWidget(box_widget_wh, 0, 1)
        layout.addWidget(box_widget_control, 1, 1)
        self.viewer_dh = My_2D_Track_Graph_Widget(
            name="DH View",
            scene_x_min=self.scene_min.d, scene_y_min=self.scene_min.h,
            scene_x_size=self.scene_size.d, scene_y_size=self.scene_size.h,
            view_scale=self.view_scale
        )
        self.viewer_dw = My_2D_Track_Graph_Widget(
            name="DW View",
            scene_x_min=self.scene_min.d, scene_y_min=self.scene_min.w,
            scene_x_size=self.scene_size.d, scene_y_size=self.scene_size.w,
            view_scale=self.view_scale
        )
        self.viewer_wh = My_2D_Track_Graph_Widget(
            name="WH View",
            scene_x_min=self.scene_min.w, scene_y_min=self.scene_min.h,
            scene_x_size=self.scene_size.w, scene_y_size=self.scene_size.h,
            view_scale=self.view_scale
        )
        self.control = My_3D_Control_Widget(self)
        layout_dh = QHBoxLayout(box_widget_dh)
        layout_dw = QHBoxLayout(box_widget_dw)
        layout_wh = QHBoxLayout(box_widget_wh)
        layout_control = QHBoxLayout(box_widget_control)
        layout_dh.addWidget(self.viewer_dh)
        layout_dw.addWidget(self.viewer_dw)
        layout_wh.addWidget(self.viewer_wh)
        layout_control.addWidget(self.control)
        self.tracks = []
        # event traps
        self.viewer_dh.hook_zoom = self.control.callback_zoom
        self.viewer_dw.hook_zoom = self.control.callback_zoom
        self.viewer_wh.hook_zoom = self.control.callback_zoom
        self.viewer_dh.hook_transfer = self.control.callback_transfer
        self.viewer_dw.hook_transfer = self.control.callback_transfer
        self.viewer_wh.hook_transfer = self.control.callback_transfer
        self.viewer_dh.hook_center = self.control.callback_center
        self.viewer_dw.hook_center = self.control.callback_center
        self.viewer_wh.hook_center = self.control.callback_center
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
        if track_3d in self.tracks:
            self.tracks.remove(track_3d)
            self.viewer_dh.remove_track(track_3d.track_dh)
            self.viewer_dw.remove_track(track_3d.track_dw)
            self.viewer_wh.remove_track(track_3d.track_wh)
        pass

    def set_zoom(self, zoom: float):
        self.zoom = zoom
        self.viewer_dh.set_zoom(zoom)
        self.viewer_dw.set_zoom(zoom)
        self.viewer_wh.set_zoom(zoom)
        # repair the origin as we changed in when zoom
        self.scene_origin = Point_3D(
            # actually, we have different way to do it with 2d-viewers x/y
            self.viewer_dh.scene_origin_2d.x(),
            self.viewer_dw.scene_origin_2d.y(),
            self.viewer_wh.scene_origin_2d.y()
        )
        pass

    def set_scene_origin(self, origin: Point_3D):
        self.scene_origin = origin
        self.viewer_dh.set_scene_origin(x=origin.d, y=origin.h)
        self.viewer_dw.set_scene_origin(x=origin.d, y=origin.w)
        self.viewer_wh.set_scene_origin(x=origin.w, y=origin.h)
        pass


if __name__ == "__main__":
    import sys
    from my_widgets import My_Main_Window
    from PyQt5.QtCore import Qt, QThread
    from PyQt5.QtWidgets import QApplication
    from my_environment import Lissajous_3D_Gen

    app = QApplication(sys.argv)

    # viewer_3d = My_3D_Viewer_Widget(view_box=Point_3D(500, 250, 250), scene_origin=Point_3D(0, 0, 0), scene_scale=1.0)
    m = 10
    scene_min = Point_3D(-250*m, -250*m, 0*m)
    scene_size = Point_3D(500*m, 500*m, 250*m)
    view_scale = 1/m * 0.75
    viewer_3d = My_3D_Viewer_Widget(scene_min=scene_min, scene_size=scene_size, view_scale=view_scale)
    # viewer_3d.set_zoom(1.0)
    # viewer_3d.show()

    window = My_Main_Window("Main Window")
    window.setCentralWidget(viewer_3d)
    window.show()

    # center = Point_3D(250, 125, 125)
    center = scene_min.add(scene_size.scale(0.5))
    amplitude = scene_size.scale(0.4)
    freq = Point_3D(1.0, 2.1, 4.1)
    phase = Point_3D(0.0, 0.0, 3.14/2)
    obj = Lissajous_3D_Gen("Gen", center, amplitude, freq, phase)

    track = viewer_3d.add_new_track("X1", Qt.red, obj.get_position())
    track.set_tail_len(100)
    track0 = viewer_3d.add_new_track("X0", Qt.green, Point_3D(0, 0, 0))
    trackС = viewer_3d.add_new_track("XС", Qt.blue, center)

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
