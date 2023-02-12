import io
import sys

# https://pypi.org/project/folium/
import folium

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from folium.plugins import MousePosition


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_window()
        self.view = None

    def init_window(self):
        self.setWindowTitle(self.tr("MAP PROJECT"))
        self.setFixedSize(1500, 800)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(10, 10, 10, 10)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)
        lay.addWidget(self.view, stretch=1)

        print("AAA")
        map = folium.Map(
            location=[55.75, 37.65],
            zoom_start=10,
            control_scale=True,
            tiles='Stamen Terrain'
            # tiles='OpenStreetMap'
            # tiles='Stamen Toner'
        )
        print("map=", map)
        print("map.get_root()=", map.get_root())
        html_str = map.get_root().render()
        print("html size=", len(html_str))
        self.view.setHtml(html_str)

        radar = folium.map.FeatureGroup()
        radar.add_child(
            folium.features.CircleMarker(
                location=(55.70, 37.60),
                popup="Radar",
                tooltip="Active",
                radius=5, color='red', fill_color='Red'
            )
        )
        map.add_child(radar)

        formatter = "function(num) {return L.Util.formatNum(num, 5);};"
        mouse_position = MousePosition(
            position='topright',
            separator=' Long: ',
            empty_string='NaN',
            lng_first=False,
            num_digits=20,
            prefix='Lat:',
            lat_formatter=formatter,
            lng_formatter=formatter,
        )
        map.add_child(mouse_position)

        # data = io.BytesIO()
        # map.save(data, close_file=False)
        # self.view.setHtml(data.getvalue().decode())

        html_str = map.get_root().render()
        print("html size=", len(html_str))
        self.view.setHtml(html_str)

        self.view.setHtml(html_str)

        print("DDD")


if __name__ == "__main__":
    # mp = folium.Map(
    #     location=[55.75, 37.65],
    #     zoom_start=10,
    #     control_scale=True,
    #     tiles='Stamen Terrain'
    #     # tiles='Stamen Toner'
    # )
    # mp.save("aaa.html", close_file=True)

    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())

