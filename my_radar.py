# Radar messages structures
import time

from copy import deepcopy
from math import sqrt, sin, cos
from operator import mod

from PyQt5.QtCore import Qt, QThread

from my_ip_service import UDP_Service_For_Radar
from point_3d import Point_3D, Point_3D_Polar
from radar_messages import RMM_Radar_Net_Address_Setup, RM_Message, RMM_Radar_North_Corner_Setup, \
    RMM_Radar_Parameter_Setup, RMM_Radar_Tx_Switch_Control, RMM_Radar_Net_Address_Status, RM_Target_Data, \
    RMM_Track_Message


class My_Radar_Track_Point:
    def __init__(self):
        self.valid_value = False
        self.new_value = False
        self.track_lot = 0
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.msec = 0
        self.distance = 0
        self.azimuth = 0
        self.elevation = 0
        self.speed = 0
        self.radial_speed = 0
        self.track_length = 0
        pass

    def print(self, msg):
        print("My_Radar_Track_Point: ", msg)
        print("  valid_value={0}, new_value={1}, ".format(self.valid_value, self.new_value))
        print("  track_lot={0}, track_length={1}".format(self.track_lot, self.track_length))
        print("  hour={0}, min={1}, sec={2}, msec={3}".format(self.hour, self.min, self.sec, self.msec))
        print("  distance={0:.1f}, azimuth={1:.2f}°, elevation={2:.2f}°".format(
            self.distance, self.azimuth*180/3.14159, self.elevation*180/3.14159
        ))
        print("  speed={0:.1f}, radial_speed={1:.1f}".format(self.speed, self.radial_speed))
        pass
    pass  # class


class My_Radar(QThread):
    def __init__(self):
        super().__init__()
        # radar parameters - might be setup with ip messages
        self.radar_ip_address = ("127.0.0.1", 10003)  # is to be local address
        self.office_ip_address = ("127.0.0.2", 10006)
        self.radar_north_angle = 0.0/180*3.14159
        self.radar_azimuth_scan_angle = 30/180*3.14159            # default azimuth scan mode 0x00
        self.radar_aperture_start_azimuth = (360-60)/180*3.14159  # aka phase sweep start angle
        self.radar_aperture_end_azimuth = 60/180*3.14159          # aka phase sweep start angle
        self.radar_aperture_start_elevation = -60/180*3.14159     # aka ?
        self.radar_aperture_end_elevation = +60/180*3.14159       # aka ?
        self.radar_tx_switch = RM_Message.ON
        self.radar_working_scene = RM_Message.GRASSLAND
        self.radar_frequency = RM_Message.FP_16G1
        # radar communication parameters and class members
        self.radar_message_send_period_ms = 10
        self.ip_service = UDP_Service_For_Radar()
        self.ip_service.ping_timeout_sec = 5.0     # listen_for_connections() message timeout
        self.ip_service.recv_timeout_sec = 1.0     # recv() message timeout
        self.ip_service.client_forget_count = 10  # the number of ping timeout to forget a client
        # class members - usually, they should not be use outside
        self.track_points = []
        pass

    def check_aperture(self, position: Point_3D):  # mathematics may be wrong here !!!
        # print("Radar aperture: azimuth: {0:.2f}° to {1:.2f}°, elevation: {2:.2f}° to {3:.2f}°".format(
        #     self.radar_aperture_start_azimuth * 180 / 3.14159, self.radar_aperture_end_azimuth * 180 / 3.14159,
        #     self.radar_aperture_start_elevation * 180 / 3.14159, self.radar_aperture_end_elevation * 180 / 3.14159
        # ))
        position_polar = Point_3D_Polar().move_to_point_3d(position)
        # position_polar.print("Point position")
        if self.radar_aperture_start_azimuth < self.radar_aperture_end_azimuth:
            if (position_polar.a < self.radar_aperture_start_azimuth) and \
               (position_polar.a > self.radar_aperture_end_azimuth):
                return False
        else:
            if (position_polar.a < self.radar_aperture_start_azimuth) and \
               (position_polar.a > self.radar_aperture_end_azimuth):
                return False
        if position_polar.e < self.radar_aperture_start_elevation:
            return False
        if position_polar.e > self.radar_aperture_end_elevation:
            return False
        return True
        pass

    def add_track_point(self, track_id, time_s, position: Point_3D, speed: Point_3D):
        # print("Adding point to track {0}".format(track_id))
        if not self.check_aperture(position):
            # print("Point {0} is out of aperture".format(track_id))
            return
        found = False
        track_point: My_Radar_Track_Point
        for track_point in self.track_points:
            if track_point.track_lot == track_id:
                track_point.track_length += 1
                found = True
                # print("{0}: Track {1} is found".format(time.time(), track_id))
                break
        if not found:
            # print("{0}: Track {1} NOT found!!!".format(time.time(), track_id))
            track_point = My_Radar_Track_Point()
            track_point.track_lot = track_id
            track_point.track_length = 1
            self.track_points.append(track_point)
        position_polar = Point_3D_Polar().move_to_point_3d(position)
        # position_polar.set_from_point_3d(position)
        spd = sqrt(speed.d*speed.d+speed.w*speed.w+speed.h*speed.h)
        radial_spd = speed.h*sin(position_polar.e) + \
                     speed.d*cos(position_polar.e)*cos(position_polar.a) + \
                     speed.w*cos(position_polar.e)*sin(position_polar.a)  # mathematics may be wrong here !!!
        track_point.hour = mod(int(time_s/3600), 24)
        track_point.min = mod(int(time_s/60), 60)
        track_point.sec = mod(int(time_s), 60)
        track_point.msec = mod(int(time_s*1000), 1000)
        track_point.distance = position_polar.r
        track_point.azimuth = position_polar.a
        track_point.elevation = position_polar.e
        track_point.speed = spd
        track_point.radial_speed = radial_spd
        track_point.new_value = True
        track_point.valid_value = True
        # print("{0}: Track {1} point added".format(time.time(), track_id))
        pass

    def create_track_message(self) -> RMM_Track_Message:
        tracks_msg_data = []
        track_point: My_Radar_Track_Point
        for track_point in self.track_points:
            if track_point.new_value and track_point.valid_value:
                track_point.new_value = False
                track_msg_data = RM_Target_Data()
                track_msg_data.type_name = "Track"+str(track_point.track_lot)
                track_msg_data.track_lot.set(track_point.track_lot)
                track_msg_data.time_hour.set(track_point.hour)
                track_msg_data.time_minutes.set(track_point.min)
                track_msg_data.time_seconds.set(track_point.sec)
                track_msg_data.time_milliseconds.set(track_point.msec)
                track_msg_data.distance.set(track_point.distance)
                track_msg_data.azimuth.set(track_point.azimuth*18000/3.14159)  # convert to 0.01 gr
                track_msg_data.zenith_angle.set(9000+track_point.elevation*18000/3.14159)  # convert to 0.01 gr
                track_msg_data.set_track_status(
                    n_of_tracking_targets=1,
                    track_status=RM_Message.TS_TWS
                )
                # track_msg_data.pitch.value.set( )  # reserved
                track_msg_data.speed.set(track_point.speed*5)                 # convert to 0.2 m/s
                track_msg_data.radial_speed.set(track_point.radial_speed*10)  # convert to 0.1 m/s, sign might be wrong
                track_msg_data.heading.set(0.0)                # convert to 0.01 gr, what is heading?
                # track_msg_data.course_shortcut.value.set()  # reserved
                track_msg_data.target_attributes.set(RM_Message.TA_UNKNOWN)
                track_msg_data.set_track_markings(
                    end_of_track=0,
                    track_acceptance=1,
                    track_quality=0x1F
                )
                track_msg_data.track_length.set(track_point.track_length)
                tracks_msg_data.append(track_msg_data)
            else:
                # print("{0}: my_radar: track_point {1}: new_value={2}, valid_value={3}".format(
                #     time.time(),
                #     track_point.track_lot, track_point.new_value, track_point.valid_value)
                # )
                # exit(-1)
                pass
        # if len(tracks_msg_data) == 0:
        #     return None
        msg = RMM_Track_Message(tracks_msg_data)
        msg.update()
        return msg

    def run(self):
        # self.ip_service.start_server()
        self.ip_service.this_ip_address = ("127.0.0.1", self.radar_ip_address[1])  # is to be local address
        self.ip_service.that_ip_address = self.office_ip_address
        self.ip_service.start_multi_client_server()
        while True:
            msg = self.create_track_message()
            self.ip_service.send_message(msg)
            self.msleep(self.radar_message_send_period_ms)


#############################
if __name__ == "__main__":
    # import time

    radar = My_Radar()
    radar.send_period_ms = 100
    radar.start()
    print("Radar started!")

    i = 0
    while True:
        x = 500/2 + 100*sin(3.14/100*i)
        y = 250/2 + 100*sin(3.14/200*i)
        z = 250/2 + 100*sin(3.14/300*i)
        t = time.time()
        radar.add_track_point(track_id=5, time_s=t, position=Point_3D(x, y, z), speed=Point_3D(10, 2, 0))
        radar.add_track_point(track_id=7, time_s=t, position=Point_3D(x, z, y), speed=Point_3D(0, 0, 10))
        i += 1
        if mod(i, 10) == 0:
            for point in radar.track_points:
                point.print("BBB")
            print()

        time.sleep(radar.send_period_ms/1000)



