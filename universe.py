# coding=utf-8
# This is a sample Python script.
import json
import string
import sys
import time
from math import sqrt, fabs, log
from operator import mod
from random import random
from randomapi import RandomJSONRPC
from threading import Thread

from PyQt5.QtCore import QSize, Qt, QRectF, QSizeF, QThread
from PyQt5.QtGui import QColor, QColorConstants, QPen, QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QHBoxLayout, QGroupBox, \
    QGraphicsSimpleTextItem, QGraphicsLineItem
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsItem, QGraphicsEllipseItem, \
                            QGraphicsItemGroup


class My_Main_Window(QMainWindow):
    def __init__(self, title, central_widget=None):
        super().__init__()
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        height = screen_rect.height()
        width = screen_rect.width()
        self.setWindowTitle(title)
        self.move(width/8, height/8)
        if central_widget is not None:
            self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        event.accept()
        sys.exit()


class Mass_Avatar:
    def __init__(self, mass):
        super().__init__()
        self.mass = mass
        self.item = None
        self.update()
        # print("Mass_Avatar(): x={0}, y={1}, size ={2}".format(mass.x, mass.y, size))
        pass

    def update(self):
        self.destroy()
        size = self.mass.r*2
        color = self.color_scale(self.mass.m)
        if size < 1.99:
            self.item = QGraphicsRectItem(0, 0, 1, 1)
        elif size < 2.99:
            self.item = QGraphicsRectItem(0, 0, 2, 2)
        elif size < 3.99:
            self.item = QGraphicsRectItem(-1, -1, 4, 4)
        # elif size < 2:
        #     self.item = QGraphicsRectItem(-size, -size, 2*size, 2*size)
        else:
            self.item = QGraphicsEllipseItem(-size/2, -size/2, size+1, size+1)
        # self.item.setRect(-size, -size, size, size)
        self.item.setPen(QPen(color, 1.0))  # to draw circle
        self.item.setBrush(color)  # to draw inside circle
        self.item.setFlag(QGraphicsItem.ItemIsMovable)
        self.item.setPos(self.mass.x, self.mass.y)
        self.mass.universe.avatar.scene.addItem(self.item)
        pass


    def destroy(self):
        if self.item is not None:
            self.item.scene().removeItem(self.item)
        pass

    def move(self):
        self.item.setPos(self.mass.x, self.mass.y)
        pass

    def color_scale(self, m) -> QColor:
        if m <= 1:
            return Qt.blue
        elif m <= 2:
            return Qt.green
        elif m <= 3:
            return Qt.magenta
        elif m <= 4:
            return Qt.red
        elif m <= 6:
            return Qt.yellow
        elif m <= 8:
            return Qt.cyan
        elif m <= 10:
            return Qt.darkBlue
        elif m <= 20:
            return Qt.darkGreen
        elif m <= 40:
            return Qt.darkMagenta
        elif m <= 80:
            return Qt.darkRed
        elif m <= 160:
            return Qt.darkYellow
        elif m <= 320:
            return Qt.darkCyan
        else:
            return Qt.gray


class Universe_Avatar(QGraphicsView):
    def __init__(self, universe):
        super().__init__()
        self.universe = universe
        self.default_line_width = 1.0
        self.scene_margin_x = 10  # scene to view margin
        self.scene_margin_y = 10  # scene to view margin
        self.x_min = 0.0  # scene left-top coordinate
        self.y_min = 0.0  # scene left-top coordinate
        self.x_max = self.x_min + universe.width  # scene right-bottom coordinate
        self.y_max = self.y_min + universe.height  # scene right-bottom coordinate
        self.scene = QGraphicsScene(self.x_min, self.y_min, universe.width, universe.height)
        self.setFixedSize(2*self.scene_margin_x+universe.width, 2*self.scene_margin_y+universe.height)
        self.setBackgroundBrush(Qt.black)
        self.setScene(self.scene)
        # to print to file
        # self.image = QImage(self.scene.width(), self.scene.height(), QImage.Format_ARGB32_Premultiplied)
        self.image = QPixmap(self.scene.width(), self.scene.height())
        self.painter = QPainter(self.image)

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

    def save_image(self, file_name):
        print("Saving image to {0}".format(file_name))
        self.image.fill(Qt.black)
        self.scene.render(self.painter)
        self.image.save(file_name)
        pass


class Mass:
    i = 0

    def __init__(self, universe, m, x, y, vx=0.0, vy=0.0):
        Mass.i = Mass.i + 1
        self.index = Mass.i
        self.name = "Mass {0}".format(Mass.i)
        self.alife = True
        self.m = m
        self.r = sqrt(m)/2  # radius
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0.0
        self.ay = 0.0
        # self.dt = universe.dt
        self.universe = universe
        self.avatar = Mass_Avatar(self)
        pass

    def print(self, str):
        print("{0}: {1} {2}: m={3}, r={4:6.2f}, x={5}, y={6}, vx={7}, vy={8}, ax={9}, ay={10}".format(
              str, self.name, self.alife, self.m, self.r, self.x, self.y, self.vx, self.vy, self.ax, self.ay
              ))
        pass

    def to_dict(self) -> {}:
        if self.alife:
            return {
                "index": self.index,
                "name":  self.name,
                "m":     self.m,
                "r":     self.r,
                "x":     self.x,
                "y":     self.y,
                "vx":    self.vx,
                "vy":    self.vy
            }
        else:
            return None

    def from_dict(self, data: {}):
        self.index = data["index"]
        self.name = data["name"]
        self.alife = True
        self.m = data["m"]
        self.r = data["r"]
        self.x = data["x"]
        self.y = data["y"]
        self.vx = data["vx"]
        self.vy = data["vy"]
        self.ax = 0.0
        self.ay = 0.0
        # self.dt = universe.dt
        self.avatar.update()
        pass

    def fuse(self, obj):
        # name = "{0}+{1}".format(self.name, obj.index)
        m = self.m + obj.m
        px = self.m*self.vx + obj.m*obj.vx
        py = self.m*self.vy + obj.m*obj.vy
        x = (self.x*self.m + obj.x*obj.m)/m
        y = (self.y*self.m + obj.y*obj.m)/m
        vx = px/m
        vy = py/m
        obj.avatar.destroy()
        self.avatar.destroy()
        obj.alife = False
        self.alife = False
        new = Mass(universe=self.universe, m=m, x=x, y=y, vx=vx, vy=vy)
        # new.name = name
        return new

    def move(self, dt):
        self.x = self.x + self.vx*dt + self.vx*dt*dt/2
        self.y = self.y + self.vy*dt + self.vy*dt*dt/2
        self.vx = self.vx + self.ax*dt
        self.vy = self.vy + self.ay*dt
        self.avatar.move()
        # self.print("moved")
        pass


class Universe:
    def __init__(self, name, width, height):
        s_time = time.time()
        self.name = name
        self.width = width
        self.height = height
        self.default_m = 1.0
        self.gravity = 10.0  # * 10
        self.fuse_distance = 0.0  # over r1+r2
        # self.dt = 1
        self.n_of_masses = 0
        self.masses = []
        self.avatar = Universe_Avatar(self)
        self.max_v = 0.0
        self.px = 0.0
        self.py = 0.0
        # print("I")
        e_time = time.time()
        print("I: {0:.4f} sec".format(e_time-s_time))
        pass

    def save(self, json_name):
        s_time = time.time()
        f = open(json_name, 'w')
        data = [mass.to_dict() for mass in self.masses]
        json.dump(data, f, indent="  ")
        e_time = time.time()
        print("SD: {0:.4f} sec for {1} objects to {2}".format(e_time-s_time, self.n_of_masses, json_name))
        pass

    def load(self, json_name):
        s_time = time.time()
        f = open(json_name, 'r')
        data = json.load(f)
        self.clean()
        for mass in data:
            obj = Mass(universe=self, m=1, x=0, y=0)
            obj.from_dict(mass)
            self.masses.append(obj)
            self.n_of_masses += 1
        self.fuse()  # just in case
        e_time = time.time()
        print("LD: {0:.4f} sec for {1} objects from {2}".format(e_time-s_time, self.n_of_masses, json_name))
        pass

    def clean(self):
        Mass.i = 0
        self.masses = []
        self.n_of_masses = 0
        pass

    def create_n(self, objects: [dict]):
        s_time = time.time()
        for i in range(0, len(objects)):
            obj = Mass(universe=self, m=objects[i]["m"],
                       x=objects[i]["x"], y=objects[i]["y"],
                       vx=objects[i]["vx"], vy=objects[i]["vy"]
            )
            self.masses.append(obj)
            self.n_of_masses += 1
        # print("CM", self.n_of_masses)
        e_time = time.time()
        print("CM: {0:.4f} sec for {1} objects".format(e_time-s_time, self.n_of_masses))
        pass

    def create_rand(self, n, json_name=None, x=None, y=None):
        s_time = time.time()
        if json_name is not None:
            data = json.load(open(json_name, 'r'))
            lx = data["x"]
            ly = data["y"]
        else:
            if x is None:
                lx = [random()*self.width for i in range(0, n)]
            else:
                lx = x
            if y is None:
                ly = [random()*self.height for i in range(0, n)]
            else:
                ly = y
        pass
        for i in range(0, n):
            m = self.default_m
            obj = Mass(universe=self, m=m, x=lx[i], y=ly[i])
            self.masses.append(obj)
            self.n_of_masses += 1
        self.fuse()  # just in case
        e_time = time.time()
        print("CR: {0:.4f} sec for {1} objects".format(e_time-s_time, self.n_of_masses))
        pass

    def calc_accelerations(self):
        s_time = time.time()
        # x2s = [self.n_of_masses]  # x**2
        # y2s = [self.n_of_masses]  # y**2
        # for i in range(0, self.n_of_masses):
        #     x2s[i] = self.masses[i].x * self.masses[i].x
        #     y2s[i] = self.masses[i].y * self.masses[i].y
        for i in range(0, self.n_of_masses):
            self.masses[i].ax = 0.0
            self.masses[i].ay = 0.0
        for i in range(0, self.n_of_masses):
            for j in range(i+1, self.n_of_masses):
                if i == j:
                    continue
                dx = self.masses[j].x - self.masses[i].x
                dx2 = dx * dx
                dy = self.masses[j].y - self.masses[i].y
                dy2 = dy * dy
                dist2 = dx2 + dy2
                dist4 = dist2 * dist2
                # dist = sqrt(dist2)
                gravity_rel = self.gravity/dist4  # self.gravity*self.masses[i].m*self.masses[j].m/dist2
                gravity_rel_x = gravity_rel * dx * fabs(dx)
                gravity_rel_y = gravity_rel * dy * fabs(dy)
                ax_i = gravity_rel_x * self.masses[j].m
                ax_j = -gravity_rel_x * self.masses[i].m
                ay_i = gravity_rel_y * self.masses[j].m
                ay_j = -gravity_rel_y * self.masses[i].m
                self.masses[i].ax += ax_i
                self.masses[j].ax += ax_j
                self.masses[i].ay += ay_i
                self.masses[j].ay += ay_j
        # print("A")
        e_time = time.time()
        print("A: {0:.4f} sec for {1} objects".format(e_time-s_time, self.n_of_masses))
        pass

    def move(self, dt):
        s_time = time.time()
        self.max_v = 0.0
        self.px = 0.0
        self.py = 0.0
        for i in range(0, self.n_of_masses):
            self.masses[i].move(dt)
            self.px += self.masses[i].vx*self.masses[i].m
            self.py += self.masses[i].vy*self.masses[i].m
            if fabs(self.masses[i].vx) > self.max_v:
                self.max_v = fabs(self.masses[i].vx)
            if fabs(self.masses[i].vy) > self.max_v:
                self.max_v = fabs(self.masses[i].vy)
        # print("M")
        e_time = time.time()
        print("M: {0:.4f} sec, px={1}, py={2}".format(e_time-s_time, self.px, self.py))
        pass

    def fuse(self):
        s_time = time.time()
        old = self.masses
        new = []
        for i in range(0, self.n_of_masses):
            current = self.masses[i]
            if not current.alife:
                continue
            for j in range(i+1, self.n_of_masses):
                if not old[j].alife:
                    continue
                fuse_distance = self.fuse_distance + current.r + old[j].r
                if (fabs(current.x-old[j].x) < fuse_distance) and (fabs(current.y-old[j].y) < fuse_distance):
                    current = current.fuse(old[j])
                    print("*", end="")
            new.append(current)
        self.masses = new
        self.n_of_masses = len(new)
        e_time = time.time()
        print("F: {0:.4f} sec".format(e_time-s_time))
        pass

    def step(self, dt):
        s_time = time.time()
        self.calc_accelerations()
        self.move(dt)
        self.fuse()
        e_time = time.time()
        print("S: {0:.4f} sec".format(e_time-s_time))
        pass

    def print(self, str):
        print("Universe {0} of {1} masses: {2}".format(self.name, self.n_of_masses, str))
        for i in range(0, self.n_of_masses):
            self.masses[i].print("  ")
        pass


if __name__ == "__main__":

    app = QApplication(sys.argv)

    uni = Universe("Universe 1", 1000, 1000)
    uni.gravity = 1000.0
    default_dt = 0.1
    max_distance = 0.1  # will trim dt to satisfy this
    save_image = True
    save_data = True
    objects_stop_limit = 5
    sim_time_stop_limit = 10  # in sec

    window = My_Main_Window("Main Window", uni.avatar)
    window.show()

    n_of_objects = 2000
    rand_json_name = 'rand_2000_2.json'
    data_json_name = 'universe_1.json'
    # opt = "2 objects"
    # opt = "masses view"
    # opt = "generate random json from random api"    # generates rand_json_name
    # opt = "create from random json"   # generates data_json_name as well
    # opt = "create random"             # generates data_json_name as well
    opt = "create from data json"

    if opt == "2 objects":
        uni.create_n([
            {"m": 100, "x": 250.0, "y": 250.0, "vx": 0.0, "vy": 0.0},
            {"m": 1,   "x": 450.0, "y": 250.0, "vx": 0.0, "vy": 2.0},
        ])
        save_image = False
        save_data = False
        stop_limit = 1

    elif opt == "masses view":
        masses = []
        for i in range(1, 20):
            masses.append({"m": i, "x": 50+i*10, "y": 250.0, "vx": 0.0, "vy": 0.0})
        for i in range(20, 300, 10):
            masses.append({"m": i, "x": 50-40+10+i*2, "y": 300.0, "vx": 0.0, "vy": 0.0})
        for i in range(300, 700, 20):
            masses.append({"m": i, "x": 50-450+10+i*1.5, "y": 350.0, "vx": 0.0, "vy": 0.0})
        uni.create_n(masses)
        for obj in uni.masses:
            obj.print("  ")
        app.exec()

    elif opt == "generate random json from random api":
        json_name = 'rand_2000_2.json'
        api_key = "7d4ea951-3450-49ce-8f6a-e4add62831f4"
        # api_key = "b1138918-62f2-4c91-8f9a-2c5ebb9a8427"
        random_client = RandomJSONRPC(api_key)
        x = random_client.generate_integers(n=n_of_objects, min=0, max=1000).parse()
        y = random_client.generate_integers(n=n_of_objects, min=0, max=1000).parse()
        data = {"x": x, "y": y}
        f = open(rand_json_name, 'w')
        json.dump(data, f, indent="  ")
        app.exec()

    elif opt == "create from random json":
        # uni.create_rand(n=n_of_objects)
        uni.create_rand(n=n_of_objects, json_name='rand_2000_1.json')
        if save_data:
            uni.save(json_name=data_json_name)

    elif opt == "create random":
        # uni.create_rand(n=n_of_objects)
        uni.create_rand(n=n_of_objects, json_name='rand_2000_1.json')
        if save_data:
            uni.save(json_name=data_json_name)

    elif opt == "create from data json":
        uni.load(json_name=data_json_name)
        # uni.save(json_name="universe_1.json")

    else:
        print("Unknown options {0}".format(opt))
        app.exec()

    QApplication.processEvents()
    if save_image:
        uni.avatar.save_image(file_name="universe_pics/scene_init.png")
    if save_data:
        uni.save(json_name="universe_data/scene_init.json")

    cycle = 0
    dt = default_dt
    sim_time = 0.0
    last_save_time = 0.0
    last_n_of_masses = uni.n_of_masses
    n_of_masses_repeated = 0
    while True:
        cycle += 1
        sim_time += dt
        uni.step(dt)
        QApplication.processEvents()
        QThread.msleep(int(dt*100))
        if uni.max_v <= max_distance/default_dt:
            dt = default_dt
        else:
            dt = max_distance/uni.max_v
        print("Cycle {0}: {1} objects left, sim_time={2:.2f}, New dt: {3:4f} ".format(
            cycle, uni.n_of_masses, sim_time, dt
        ))
        #
        if sim_time-last_save_time > 1.0:
            if save_image:
                uni.avatar.save_image(file_name="universe_pics/scene_{0}.png".format(cycle))
            if save_data:
                uni.save(json_name="universe_data/scene_{0}.json".format(cycle))
            last_save_time = sim_time
        #
        if last_n_of_masses == uni.n_of_masses:
            n_of_masses_repeated += 1
        else:
            n_of_masses_repeated = 0
            last_n_of_masses = uni.n_of_masses
        if (n_of_masses_repeated > 25) and (uni.n_of_masses < 10):
            n_of_masses_repeated = 0
            uni.print("Cycle {0}".format(cycle))
        #
        if uni.n_of_masses <= objects_stop_limit:
            print("Finish simulation - the universe has collapsed to a {0} objects!".format(uni.n_of_masses))
            uni.print("Cycle {0}".format(cycle))
            app.exec()
        if sim_time >= sim_time_stop_limit:
            print("Finish simulation - simulation time expired {0}!".format(sim_time_stop_limit))
            uni.print("Cycle {0}".format(cycle))
            app.exec()
    pass

        # points = random_client.generate_integers(n=2*n_of_points, min=0, max=window.width).parse()
        # print(".", end="")
        # sys.stdout.flush()
        # for i in range(0, n_of_points):
        #     x = points[i*2]
        #     y = points[i*2+1]
        #     x = random()*window.width
        #     y = random()*window.hight
        #     window.graph.add_point(x, y)
        #     QApplication.processEvents()
        #     QThread.msleep(10)

    app.exec()
