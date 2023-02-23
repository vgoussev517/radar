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

    def set(self, val):
        val_int = int(val)
        if self.size == 1:
            self.value = val_int & 0xFF
        elif self.size == 2:
            self.value = val_int & 0xFFFF
        elif self.size == 4:
            self.value = val_int & 0xFFFFFFFF
        elif self.size == 3:
            self.value = val_int & 0xFFFFFF
        elif self.size == 0:
            pass
        else:
            mask = 0xFFFFFFFF
            for i in range(4, self.size):
                mask = (mask << 8) | 0xFF
            self.value = val_int & mask
        pass

    pass  # class


class RM_Fields:  # just a group of fields
    def __init__(self):
        self._fields = []
        self.type_name = "RM_Fields"

    def define(self, name, size, order, value) -> RM_Field_Record:
        field = RM_Field_Record(name, size, order, value)
        self._fields.append(field)
        return field

    def calc_length(self) -> int:
        length = 0
        for field in self._fields:
            length = length + field.size
        return length

    def print(self, msg):
        print("{0}: {1}".format(self.type_name, msg))
        print("  actual Length={0} (0x{0:X})".format(self.calc_length()))
        for field in self._fields:
            field.print("  ")
        pass


class RM_Message (RM_Fields):
    START_ID = 0xAA
    MT_NET_ADDR_SETUP = 0x5C      # message type
    MT_NORTH_CORNER_SETUP = 0x53  # message type
    MT_PARAMETER_SETUP = 0x52     # message type
    MT_TX_SWITCH_CTRL = 0x54      # message type
    MT_NET_ADDR_STATUS = 0x79     # message type
    MT_TRACK_MESSAGE = 0x76       # message type
    MT_NEW = 0x00                 # message type (for new packets)
    MLEN_NET_ADDR_SETUP = 32      # message length
    MLEN_NORTH_CORNER_SETUP = 16    # message length
    MLEN_PARAMETER_SETUP = 24       # message length
    MLEN_TX_SWITCH_CTRL = 8         # message length
    MLEN_NET_ADDR_STATUS = 32       # message length
    MLEN_TRACK_MESSAGE = 10         # message length
    MLEN_NEW = 0                    # message length (for new packets)
    MLEN_TARGET = 32                # length of target data
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
        super().__init__()
        self.type_name = "RM_Message"
        self.start_id =  self.define("Start identification", 1, RM_Field_Record.BE, RM_Message.START_ID)
        self.type =      self.define("Message type",         1, RM_Field_Record.BE, RM_Message.MT_NEW)
        self.length =    self.define("Message length",       2, RM_Field_Record.BE, RM_Message.MLEN_NEW)
        # self.checksum =  self.define("Checksum",             1, RM_Field_Record.BE, 0x00)
        self.checksum = None

    def add_fields(self, fields: RM_Fields):
        pass

    def print(self, msg):
        print("{0}: {1}".format(self.type_name, msg))
        print("  actual Length={0} (0x{0:X}), actual length Checksum=0x{1:X}".
              format(self.calc_length(), self.calc_checksum()))
        for field in self._fields:
            field.print("  ")
        pass

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

    def pack(self) -> bytes:
        byte_msg = bytearray(self.length.value)
        i = 0
        for field in self._fields:
            # field.print("pack(self): ")  # !!!
            val = field.value
            if field.size == 1:
                byte_msg[i] = val & 0xFF
                # print("  i={0}, byte_msg[j]={1}, val={2}".format(i, byte_msg[i], val))
                i += 1
            elif field.size == 0:
                pass
            else:
                if field.order == RM_Field_Record.LE:
                    for j in range(i, i+field.size, 1):
                        byte_msg[j] = val & 0xFF
                        val = val >> 8
                else:
                    for j in range(i+field.size-1, i-1, -1):
                        byte_msg[j] = val & 0xFF
                        # print("  j={0}, byte_msg[j]={1}, val={2}".format(j, byte_msg[j], val))
                        val = val >> 8
                i = i + field.size
        if i != self.length.value:
            print("ERROR: RM_Message.pack(): the length field ({0}) is not equal to the actual length ({1})".format(
                self.length.value, i
            ))
        return byte_msg
        pass

    def unpack(self, byte_msg: bytes):
        i = 0
        for field in self._fields:
            # field.print("unpack(before): ")  # !!!
            if field.size == 1:
                field.value = byte_msg[i]
                # print("  i={0}, byte_msg[i]={1}, val={2}".format(i, byte_msg[i], field.value))
                i += 1
            elif field.size == 0:
                pass
            else:
                val = 0
                if field.order == RM_Field_Record.LE:
                    for j in range(i+field.size-1, i-1, -1):
                        val = (val << 8) + byte_msg[j]
                        # print("  j={0}, byte_msg[j]={1}, val={2}".format(j, byte_msg[j], val))
                else:
                    for j in range(i, i+field.size, 1):
                        val = (val << 8) + byte_msg[j]
                        # print("  j={0}, byte_msg[j]={1}, val={2}".format(j, byte_msg[j], val))
                field.value = val
                i = i + field.size
            # field.print("unpack(after): ")  # !!!
        if i != self.length.value:
            print("ERROR: RM_Message.pack(): the length field ({0}) is not equal to the actual length ({1})".format(
                self.length.value, i
            ))
        pass


# ----------------------- to Radar ---------------------------------------------
# IP and Port Number Configuration Saving Messages
class RMM_Radar_Net_Address_Setup (RM_Message):
    def __init__(self, radar_net_port, radar_net_ip, terminal_net_port, terminal_net_ip, saving_order):
        super().__init__()
        self.type_name = "RMM_Radar_Net_Address_Setup"
        # self.start_id
        self.type.set(RM_Message.MT_NET_ADDR_SETUP)
        self.length.set(RM_Message.MLEN_NET_ADDR_SETUP)
        self.pkt_num              = self.define("Packet number",        2, RM_Field_Record.BE, 0x0000)
        self.radar_net_port       = self.define("Radar net port",       2, RM_Field_Record.BE, radar_net_port)
        self.radar_net_ip         = self.define("Radar net ip",         4, RM_Field_Record.BE, radar_net_ip)
        self.terminal_net_port    = self.define("Terminal net port",    2, RM_Field_Record.BE, terminal_net_port)
        self.terminal_net_ip      = self.define("Terminal net ip",      4, RM_Field_Record.LE, terminal_net_ip)
        self.saving_order         = self.define("Saving order",         1, RM_Field_Record.BE, saving_order )
        self.backups              = self.define("backups",             12, RM_Field_Record.BE, 0)
        self.checksum             =  self.define("Checksum",            1, RM_Field_Record.BE, 0x00)


# Saving messages in the main north corner
class RMM_Radar_North_Corner_Setup (RM_Message):
    def __init__(self, north_corner, saving_method, saving_order):
        super().__init__()
        self.type_name = "RMM_Radar_North_Corner_Setup"
        # self.start_id
        self.type.set(RM_Message.MT_NORTH_CORNER_SETUP)
        self.length.set(RM_Message.MLEN_NORTH_CORNER_SETUP)
        self.pkt_num              = self.define("Packet number",        2, RM_Field_Record.BE, 0x0000)
        self.north_corner         = self.define("North Corner",         2, RM_Field_Record.BE, north_corner)
        self.saving_method        = self.define("Saving method",        1, RM_Field_Record.BE, saving_method)
        self.saving_order         = self.define("Saving order",         1, RM_Field_Record.BE, saving_order)
        self.backups              = self.define("backups",              5, RM_Field_Record.BE, 0)
        self.checksum             =  self.define("Checksum",            1, RM_Field_Record.BE, 0x00)


# Radar parameter setting
class RMM_Radar_Parameter_Setup (RM_Message):
    def __init__(self, scene, frequency, phase_sweep_start, phase_sweep_end, saving_order):
        super().__init__()
        self.type_name = "RMM_Radar_Parameter_Setup"
        # self.start_id
        self.type.set(RM_Message.MT_PARAMETER_SETUP)
        self.length.set(RM_Message.MLEN_PARAMETER_SETUP)
        self.pkt_num              = self.define("Packet number",             2, RM_Field_Record.BE, 0x0000)
        self.azimuth_scan_mode    = self.define("Azimuth scan mode (3 lsb)", 1, RM_Field_Record.BE, RM_Message.PHASE & 0x07)
        self.scene                = self.define("Radar scene (3 lsb)",       1, RM_Field_Record.BE, scene & 0x07)
        self.frequency            = self.define("Radar frequency (4 lsb)",   1, RM_Field_Record.BE, frequency & 0x0F)
        self.phase_sweep_start    = self.define("Phase sweep start",         2, RM_Field_Record.BE, phase_sweep_start)
        self.phase_sweep_end      = self.define("Phase sweep end",           2, RM_Field_Record.BE, phase_sweep_end)
        self.saving_order         = self.define("Saving order",              1, RM_Field_Record.BE, saving_order)
        self.backups              = self.define("backups",                   9, RM_Field_Record.BE, 0)
        self.checksum             =  self.define("Checksum",                 1, RM_Field_Record.BE, 0x00)


# Transmitting switch control
class RMM_Radar_Tx_Switch_Control (RM_Message):
    def __init__(self, transmit_switch):
        super().__init__()
        self.type_name = "RMM_Radar_Tx_Switch_Control"
        # self.start_id
        self.type.set(RM_Message.MT_TX_SWITCH_CTRL)
        self.length.set(RM_Message.MLEN_TX_SWITCH_CTRL)
        self.pkt_num              = self.define("Packet number",             2,  RM_Field_Record.BE, 0x0000)
        self.transmit_switch      = self.define("Transmit switch (1 lsb)",   1, RM_Field_Record.BE, transmit_switch)
        self.checksum             =  self.define("Checksum",                 1, RM_Field_Record.BE, 0x00)


# ----------------------- from Radar ---------------------------------------------
# IP and Port Number Configuration Status
class RMM_Radar_Net_Address_Status (RM_Message):
    def __init__(self, radar_net_port, radar_net_ip, terminal_net_port, terminal_net_ip):
        super().__init__()
        self.type_name = "RMM_Radar_Net_Address_Status"
        # self.start_id
        self.type.set(RM_Message.MT_NET_ADDR_STATUS)
        self.length.set(RM_Message.MLEN_NET_ADDR_STATUS)
        self.pkt_num              = self.define("Packet number",        2, RM_Field_Record.BE, 0x0000)
        self.radar_net_port       = self.define("Radar net port",       2, RM_Field_Record.BE, radar_net_port)
        self.radar_net_ip         = self.define("Radar net ip",         4, RM_Field_Record.BE, radar_net_ip)
        self.terminal_net_port    = self.define("Terminal net port",    2, RM_Field_Record.BE, terminal_net_port)
        self.terminal_net_ip      = self.define("Terminal net ip",      4, RM_Field_Record.LE, terminal_net_ip)
        self.backups              = self.define("backups",             13, RM_Field_Record.BE, 0)
        self.checksum             =  self.define("Checksum",            1, RM_Field_Record.BE, 0x00)


# Track Message
class RM_Target_Data (RM_Fields):
    def __init__(self):
        super().__init__()
        self.track_lot         = self.define("Track lot",             2, RM_Field_Record.BE, 0x0000)  # 1 to 256
        self.reserved_8        = self.define("reserved 8",            1, RM_Field_Record.BE, 0x00)
        self.time_hour         = self.define("Hour",                  1, RM_Field_Record.BE, 0x00)    # 0 to 23
        self.time_minutes      = self.define("Minutes",               1, RM_Field_Record.BE, 0x00)    # 0 to 59
        self.time_seconds      = self.define("Seconds",               1, RM_Field_Record.BE, 0x00)    # 0 to 59
        self.time_milliseconds = self.define("Milliseconds",          2, RM_Field_Record.BE, 0x0000)  # 0 to 999
        self.zenith_angle      = self.define("Zenith angle!?, .01°",  2, RM_Field_Record.BE, 0x0000)  # 0° to 360° in .01°
        self.reserved_16_18    = self.define("reserved 16~18",        3, RM_Field_Record.BE, 0x000000)
        self.track_status      = self.define("Track status",          1, RM_Field_Record.BE, RM_Message.TS_TWS)
        self.distance          = self.define("Distance!, m",          2, RM_Field_Record.BE, 0x0000)  # 0 to 30000 m
        self.azimuth           = self.define("Azimuth!, .01°",        2, RM_Field_Record.BE, 0x0000)  # 0° to 360° in .01°
        self.pitch             = self.define("Pitch (reserved)",      2, RM_Field_Record.BE, 0x0000)  # -150 to 1500 mil in *
        self.speed             = self.define("Speed!, 0.2m/s",        2, RM_Field_Record.BE, 0x0000)  # 0 to 500 m/s
        self.heading           = self.define("Heading!?, .01°",       2, RM_Field_Record.BE, 0x0000)  # 0° to 360° in .01°
        self.course_shortcut   = self.define("Course shortcut (res)", 2, RM_Field_Record.BE, 0x0000)  # 0 to 30000 m
        self.radial_speed      = self.define("Radial speed, 0.1m/s",  2, RM_Field_Record.BE, 0x0000)  # -500 to 500 m/s in 0.1 m/s
        self.target_attributes = self.define("Target attributes",     1, RM_Field_Record.BE, RM_Message.TA_UNKNOWN)
        self.track_markings    = self.define("Track markings",        1, RM_Field_Record.BE, 0x00)
        self.track_length      = self.define("Track length",          2, RM_Field_Record.BE, 0x0000)
        pass

    def set_track_status(self, n_of_tracking_targets, track_status):
        self.track_status = track_status & 0x07 + ((n_of_tracking_targets & 0x1F) << 3)
        pass

    def set_track_markings(self, end_of_track, track_acceptance, track_quality):
        self.track_markings = track_quality & 0x1F + ((track_acceptance & 0x01) << 5) + ((end_of_track & 0x01) << 6)
        pass


# create RMM_Track_Message first, add RM_Track_Data then
class RMM_Track_Message (RM_Message):
    def __init__(self, targets: [RM_Target_Data]):
        super().__init__()
        self.targets = []
        number_of_targets = len(targets) & 0xFF
        self.type_name = "RMM_Track_Message"
        # self.start_id
        self.type.set(RM_Message.MT_TRACK_MESSAGE)
        self.length.set(RM_Message.MLEN_TRACK_MESSAGE+RM_Message.MLEN_TARGET*number_of_targets)
        self.pkt_num              =  self.define("Packet number",             1, RM_Field_Record.BE, 0x00)  # only 1 byte?
        self.n_of_targets         =  self.define("Number of targets",         1, RM_Field_Record.BE, number_of_targets)
        for i in range(0, number_of_targets):
            self._add_target(deepcopy(targets[i]), i)  # we want to avoid references here
        self.backups              =  self.define("backups",                   3, RM_Field_Record.BE, 0)
        self.checksum             =  self.define("Checksum",                  1, RM_Field_Record.BE, 0x00)
        pass

    def _add_target(self, target: RM_Target_Data, i: int):
        self.targets.append(target)
        self.define("Track data --------------- "+str(i), 0, RM_Field_Record.BE, 0)
        for field in target._fields:
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
    targets = []
    for i in range(0, 3):
        target = RM_Target_Data()
        target.track_lot = i*10+1
        targets.append(target)
    msg_track = RMM_Track_Message(targets)
    end_time = time.time()
    msg_track.print("This message: ")
    msg_track.update()
    msg_track.print("Updated message: ")
    print('RMM_Track_Message create time: ', end_time-start_time)

    x = msg_track.pack()
    print("Packed: ", x)
    msg_track.unpack(x)
    msg_track.print("Unpacked: ")

