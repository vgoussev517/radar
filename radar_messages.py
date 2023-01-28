# Radar messages structures
from copy import deepcopy


class RM_Field_Record:
    BE = 0
    LE = 1

    def __init__(self, name, size, order, value):
        self.name = name
        self.size = size
        self.order = order
        self.value = value

    def print(self, ident):
        print("{0}{1:28} size={2:>3},  value=0x{3:X}".format(ident, self.name+":", self.size, self.value))
        pass


class RM_Message:
    BE = RM_Field_Record.BE
    LE = RM_Field_Record.LE
    NO_BIND = 0x00     # saving order
    BIND = 0x01        # saving order
    AUTO = 0x00        # saving method
    MANUAL = 0x01      # saving method
    PHASE = 0x00       # Azimuth scan mode
    GOBI = 0x00        # Radar scenes (global work)
    GRASSLAND = 0x01   # Radar scenes (global work)
    LAKES = 0x01       # Radar scenes (global work)
    JUNGLES = 0x01     # Radar scenes (global work)
    RAIN_SNOW = 0x01   # Radar scenes (global work)
    FP_15G9 = 0x00     # Radar frequency (GHz)
    FP_16G1 = 0x01     # Radar frequency (GHz)
    FP_16G3 = 0x02     # Radar frequency (GHz)
    FP_16G5 = 0x03     # Radar frequency (GHz)
    FP_16G7 = 0x04     # Radar frequency (GHz)
    OFF = 0x00         # Transmit switch
    ON = 0x01          # Transmit switch
    TS_TWS = 0x01      # Track status
    TS_TASS = 0x02     # Track status
    TS_TAST = 0x03     # Track status
    TS_GAZE = 0x04     # Track status
    TA_UNKNOWN = 0x00           # Target attributed
    TA_SINGLE_PERSON = 0x01     # Target attributed
    TA_MULTIPLE_PERSONS = 0x02  # Target attributed
    TA_VEHICLE = 0x03           # Target attributed
    TA_LARGE_BOATS = 0x04       # Target attributed
    TA_BICYCLES = 0x05          # Target attributed
    TA_DRONES = 0x06            # Target attributed
    TA_UNKNOWN_8 = 0x08         # Target attributed
    TA_SMALL_BOATS = 0x09       # Target attributed
    TA_MEDIUM_BOAT = 0x0A       # Target attributed
    TA_LARGE_BOAT = 0x0B        # Target attributed

    def __init__(self):
        self._fields = []
        self.type_name = "RM_Message"
        self.start_id = None
        self.type = None
        self.length = None
        self.pkt_num = None
        self.checksum = None

    def define(self, name, size, order, value) -> RM_Field_Record:
        field = RM_Field_Record(name, size, order, value)
        self._fields.append(field)
        return field

    def add_field_list(self, field_list):
        pass

    def print(self, msg):
        print("{0}: {1}".format(self.type_name, msg))
        print("  actual Length={0} (0x{0:X}), actual length Checksum=0x{1:X}".
              format(self.calc_length(), self.calc_checksum()))
        for field in self._fields:
            field.print("  ")
        pass

    def calc_length(self) -> int:
        length = 0
        for field in self._fields:
            length = length + field.size
        return length

    def calc_checksum(self) -> int:
        checksum = 0
        for field in self._fields:
            val = field.value
            while val > 0:
                checksum = checksum + val & 0xFF
                val = val >> 8
        checksum = (checksum - self.checksum.value) & 0xFF
        return checksum

    def update(self):
        self.length.value = self.calc_length()
        self.checksum.value = self.calc_checksum()
        pass

    def pack(self) -> bytearray:
        pass

    def unpack(self, x: bytearray):
        pass


# ----------------------- to Radar ---------------------------------------------
# IP and Port Number Configuration Saving Messages
class RMM_Radar_Net_Address_Setup (RM_Message):
    def __init__(self, radar_net_port, radar_net_ip, terminal_net_port, terminal_net_ip, saving_order):
        super().__init__()
        self.type_name = "RMM_Radar_Net_Address_Setup"
        self.start_id             = self.define("Start identification", 1, self.BE, 0xAA)
        self.type                 = self.define("Message type",         1, self.BE, 0x5C)
        self.length               = self.define("Message length",       2, self.BE, 32)
        self.pkt_num              = self.define("Packet number",        2, self.BE, 0x0000)
        self.radar_net_port       = self.define("Radar net port",       2, self.BE, radar_net_port)
        self.radar_net_ip         = self.define("Radar net ip",         4, self.BE, radar_net_ip)
        self.terminal_net_port    = self.define("Terminal net port",    2, self.BE, terminal_net_port)
        self.terminal_net_ip      = self.define("Terminal net ip",      4, self.LE, terminal_net_ip)
        self.saving_order         = self.define("Saving order",         1, self.BE, saving_order )
        self.backups              = self.define("backups",             12, self.BE, 0)
        self.checksum             = self.define("Checksum",             1, self.BE, 0x00)


# Saving messages in the main north corner
class RMM_Radar_North_Corner_Setup (RM_Message):
    def __init__(self, north_corner, saving_method, saving_order):
        super().__init__()
        self.type_name = "RMM_Radar_North_Corner_Setup"
        self.start_id             = self.define("Start identification", 1, self.BE, 0xAA)
        self.type                 = self.define("Message type",         1, self.BE, 0x53)
        self.length               = self.define("Message length",       2, self.BE, 16)
        self.pkt_num              = self.define("Packet number",        2, self.BE, 0x0000)
        self.north_corner         = self.define("North Corner",         2, self.BE, north_corner)
        self.saving_method        = self.define("Saving method",        1, self.BE, saving_method)
        self.saving_order         = self.define("Saving order",         1, self.BE, saving_order)
        self.backups              = self.define("backups",              5, self.BE, 0)
        self.checksum             = self.define("Checksum",             1, self.BE, 0x00)


# Radar parameter setting
class RMM_Radar_Parameter_Setup (RM_Message):
    def __init__(self, scene, frequency, phase_sweep_start, phase_sweep_end, saving_order):
        super().__init__()
        self.type_name = "RMM_Radar_Parameter_Setup"
        self.start_id             = self.define("Start identification",      1, self.BE, 0xAA)
        self.type                 = self.define("Message type",              1, self.BE, 0x52)
        self.length               = self.define("Message length",            2, self.BE, 24)
        self.pkt_num              = self.define("Packet number",             2, self.BE, 0x0000)
        self.azimuth_scan_mode    = self.define("Azimuth scan mode (3 lsb)", 1, self.BE, self.PHASE & 0x07)
        self.scene                = self.define("Radar scene (3 lsb)",       1, self.BE, scene & 0x07)
        self.frequency            = self.define("Radar frequency (4 lsb)",   1, self.BE, frequency & 0x0F)
        self.phase_sweep_start    = self.define("Phase sweep start",         2, self.BE, phase_sweep_start)
        self.phase_sweep_end      = self.define("Phase sweep end",           2, self.BE, phase_sweep_end)
        self.saving_order         = self.define("Saving order",              1, self.BE, saving_order)
        self.backups              = self.define("backups",                   9, self.BE, 0)
        self.checksum             = self.define("Checksum",                  1, self.BE, 0x00)


# Transmitting switch control
class RMM_Radar_Tx_Switch_Control (RM_Message):
    def __init__(self, transmit_switch):
        super().__init__()
        self.type_name = "RMM_Radar_Tx_Switch_Control"
        self.start_id             = self.define("Start identification",      1, self.BE, 0xAA)
        self.type                 = self.define("Message type",              1, self.BE, 0x54)
        self.length               = self.define("Message length",            2, self.BE, 8)
        self.pkt_num              = self.define("Packet number",             2, self.BE, 0x0000)
        self.transmit_switch      = self.define("Transmit switch (1 lsb)",   1, self.BE, transmit_switch)
        self.checksum             = self.define("Checksum",                  1, self.BE, 0x00)


# ----------------------- from Radar ---------------------------------------------
# IP and Port Number Configuration Status
class RMM_Radar_Net_Address_Status (RM_Message):
    def __init__(self, radar_net_port, radar_net_ip, terminal_net_port, terminal_net_ip):
        super().__init__()
        self.type_name = "RMM_Radar_Net_Address_Status"
        self.start_id             = self.define("Start identification", 1, self.BE, 0xAA)
        self.type                 = self.define("Message type",         1, self.BE, 0x79)
        self.length               = self.define("Message length",       2, self.BE, 32)
        self.pkt_num              = self.define("Packet number",        2, self.BE, 0x0000)
        self.radar_net_port       = self.define("Radar net port",       2, self.BE, radar_net_port)
        self.radar_net_ip         = self.define("Radar net ip",         4, self.BE, radar_net_ip)
        self.terminal_net_port    = self.define("Terminal net port",    2, self.BE, terminal_net_port)
        self.terminal_net_ip      = self.define("Terminal net ip",      4, self.LE, terminal_net_ip)
        self.backups              = self.define("backups",             13, self.BE, 0)
        self.checksum             = self.define("Checksum",             1, self.BE, 0x00)


# Track Message
class RM_Track_Data (RM_Message):
    def __init__(self):
        super().__init__()
        self.track_lot         = self.define("Track lot",                      2, self.BE, 0x0000)  # 1 to 256
        self.reserved_8        = self.define("reserved 8",                     1, self.BE, 0x00)
        self.time_hour         = self.define("Hour",                           1, self.BE, 0x00)    # 0 to 23
        self.time_minutes      = self.define("Minutes",                        1, self.BE, 0x00)    # 0 to 59
        self.time_seconds      = self.define("Seconds",                        1, self.BE, 0x00)    # 0 to 59
        self.time_milliseconds = self.define("Milliseconds",                   2, self.BE, 0x0000)  # 0 to 999
        self.antenna_angle     = self.define("Antenna angle!?, gr/100",        2, self.BE, 0x0000)  # 0 to 360 gr
        self.reserved_16_18    = self.define("reserved 16~18",                 3, self.BE, 0x000000)
        self.track_status      = self.define("Track status",                   1, self.BE, self.TS_TWS)
        self.distance          = self.define("Distance!, m",                   2, self.BE, 0x0000)  # 0 to 30000 m
        self.azimuth           = self.define("Azimuth!, gr/100",               2, self.BE, 0x0000)  # 0 to 360 gr
        self.pitch             = self.define("Pitch (reserved)",               2, self.BE, 0x0000)  # -150 to 1500 mil
        self.speed             = self.define("Speed!, m/s/5",                  2, self.BE, 0x0000)  # 0 to 500 m/s
        self.heading           = self.define("Heading!, gr/100",               2, self.BE, 0x0000)  # 0 to 360 gr
        self.course_shortcut   = self.define("Course shortcut (reserved)",     2, self.BE, 0x0000)  # 0 to 30000 m
        self.radial_speed      = self.define("Radial speed, m/s/10",           2, self.BE, 0x0000)  # -500 to 500 m/s
        self.target_attributes = self.define("Target attributes",              1, self.BE, self.TA_UNKNOWN)
        self.track_markings    = self.define("Track markings",                 1, self.BE, 0x00)
        self.track_length      = self.define("Track length",                   2, self.BE, 0x0000)
        pass

    def set_track_status(self, n_of_tracking_targets, track_status):
        self.track_markings = track_status & 0x07 + ((n_of_tracking_targets & 0x1F) << 3)
        pass

    def set_track_markings(self, end_of_track, track_acceptance, track_quality):
        self.track_markings = track_quality & 0x1F + ((track_acceptance & 0x01) << 5) + ((end_of_track & 0x01) << 6)
        pass


# create RMM_Track_Message first, add RM_Track_Data then
class RMM_Track_Message (RM_Message):
    def __init__(self, tracks: [RM_Track_Data]):
        super().__init__()
        self.tracks = []
        number_of_targets = len(tracks) & 0xFF
        self.type_name = "RMM_Track_Message"
        self.start_id             = self.define("Start identification",      1, self.BE, 0xAA)
        self.type                 = self.define("Message type",              1, self.BE, 0x76)
        self.length               = self.define("Message length",            2, self.BE, 10+32*number_of_targets)
        self.pkt_num              = self.define("Packet number",             1, self.BE, 0x00)  # only 1 byte?
        self.number_of_targets    = self.define("Number of targets",         1, self.BE, number_of_targets)
        for i in range(0, number_of_targets):
            self._add_track(deepcopy(tracks[i]), i)  # we want to avoid references here
        self.backups              = self.define("backups",                   3, self.BE, 0)
        self.checksum             = self.define("Checksum",                  1, self.BE, 0x00)
        pass

    def _add_track(self, track: RM_Track_Data, i: int):
        self.tracks.append(track)
        self.define(track.type_name+" --------------- "+str(i), 0, self.BE, 0)
        for field in track._fields:
            self._fields.append(field)
        pass


#############################
if __name__ == "__main__":
    import time

    msg1 = RMM_Radar_Net_Address_Setup(radar_net_port=0x1234, radar_net_ip=0x7f000001,
                                       terminal_net_port=0x3421, terminal_net_ip=0x7f000002,
                                       saving_order=RM_Message.BIND)

    msg2 = RMM_Radar_North_Corner_Setup(north_corner=90, saving_method=RM_Message.AUTO,
                                        saving_order=RM_Message.BIND)

    msg3 = RMM_Radar_Parameter_Setup(scene=RM_Message.GRASSLAND, frequency=RM_Message.FP_16G1,
                                     phase_sweep_start=-45, phase_sweep_end=+45,
                                     saving_order=RM_Message.BIND)

    msg4 = RMM_Radar_Tx_Switch_Control(transmit_switch=RM_Message.ON)

    msg5 = RMM_Radar_Net_Address_Status(radar_net_port=0x1234, radar_net_ip=0x7f000001,
                                        terminal_net_port=0x3421, terminal_net_ip=0x7f000002)

    msg = msg5
    msg.print("This message: ")
    msg.update()
    msg.print("Updated message: ")

    start_time = time.time()
    tracks = []
    for i in range(0, 4):
        track = RM_Track_Data()
        track.track_lot = i*10+1
        tracks.append(track)
    msg_track = RMM_Track_Message(tracks)
    end_time = time.time()
    msg_track.print("This message: ")
    msg_track.update()
    msg_track.print("Updated message: ")
    print('RMM_Track_Message create time: ', end_time-start_time)


