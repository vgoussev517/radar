# Radar messages structures

class RM_Field_Record:
    BE = 0
    LE = 1

    def __init__(self, name, size, order, value):
        self.name = name
        self.size = size
        self.order = order
        self.value = value


class RM_Message:
    BE = RM_Field_Record.BE
    LE = RM_Field_Record.LE
    NO_BIND = 0x00     # saving order
    BIND = 0x01        # saving order
    AUTONOMOUS = 0x00  # saving method
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

    def __init__(self):
        self.name = "general"
        self.start_identification = 0xAA
        self.message_type = None
        self.message_length = None
        self.paket_number = None

    def pack(self) -> bytearray:
        pass

    def unpack(self, x: bytearray):
        pass

    def print(self):
        pass


# IP and Port Number Configuration Saving Messages
class RMM_Net_Address_Saving (RM_Message):
    def __init__(self, radar_net_port, radar_net_ip, terminal_net_port, terminal_net_ip, saving_order):
        super().__init__()
        self.start_identification = RM_Field_Record("Start identification", 1, self.BE, 0xAA)
        self.message_type         = RM_Field_Record("Message type",         1, self.BE, 0x5C)
        self.message_length       = RM_Field_Record("Message length",       2, self.BE, 32)
        self.paket_number         = RM_Field_Record("Packet number",        2, self.BE, 0x0000)
        self.radar_net_port       = RM_Field_Record("Radar net port",       2, self.BE, radar_net_port)
        self.radar_net_ip         = RM_Field_Record("Radar net ip",         2, self.BE, radar_net_ip)
        self.terminal_net_port    = RM_Field_Record("Terminal net port",    2, self.BE, terminal_net_port)
        self.terminal_net_ip      = RM_Field_Record("Terminal net ip",      4, self.LE, terminal_net_ip)
        self.saving_order         = RM_Field_Record("Saving order",         1, self.BE, saving_order )
        self.backups              = RM_Field_Record("backups",             12, self.BE, 0)
        self.checksum             = RM_Field_Record("Checksum",             1, self.BE, 0x00)


# Saving messages in the main north corner
class RMM_North_Corner_Setting (RM_Message):
    def __init__(self, north_corner, saving_method, saving_order):
        super().__init__()
        self.start_identification = RM_Field_Record("Start identification", 1, self.BE, 0xAA)
        self.message_type         = RM_Field_Record("Message type",         1, self.BE, 0x53)
        self.message_length       = RM_Field_Record("Message length",       2, self.BE, 16)
        self.paket_number         = RM_Field_Record("Packet number",        2, self.BE, 0x0000)
        self.north_corner         = RM_Field_Record("North Corner",         2, self.BE, north_corner)
        self.saving_method        = RM_Field_Record("Saving method",        1, self.BE, saving_method)
        self.saving_order         = RM_Field_Record("Saving order",         1, self.BE, saving_order)
        self.backups              = RM_Field_Record("backups",              5, self.BE, 0)
        self.checksum             = RM_Field_Record("Checksum",             1, self.BE, 0x00)


# Radar parameter setting
class RMM_North_Parameter_Setting (RM_Message):
    def __init__(self, scene, frequency, phase_sweep_start, phase_sweep_end, saving_order):
        super().__init__()
        self.start_identification = RM_Field_Record("Start identification",      1, self.BE, 0xAA)
        self.message_type         = RM_Field_Record("Message type",              1, self.BE, 0x52)
        self.message_length       = RM_Field_Record("Message length",            2, self.BE, 24)
        self.paket_number         = RM_Field_Record("Packet number",             2, self.BE, 0x0000)
        self.azimuth_scan_mode    = RM_Field_Record("Azimuth scan mode (3 lsb)", 1, self.BE, self.PHASE & 0x07)
        self.scene                = RM_Field_Record("Radar scene (3 lsb)",       1, self.BE, scene & 0x07)
        self.frequency            = RM_Field_Record("Radar frequency (4 lsb)",   1, self.BE, frequency & 0x0F)
        self.phase_sweep_start    = RM_Field_Record("Phase sweep start",         2, self.BE, phase_sweep_start)
        self.phase_sweep_end      = RM_Field_Record("Phase sweep end",           2, self.BE, phase_sweep_end)
        self.saving_order         = RM_Field_Record("Saving order",              1, self.BE, saving_order)
        self.backups              = RM_Field_Record("backups",                   9, self.BE, 0)
        self.checksum             = RM_Field_Record("Checksum",                  1, self.BE, 0x00)


# Transmitting switch control
class RMM_Tx_Switch_Control (RM_Message):
    def __init__(self, transmit_switch):
        super().__init__()
        self.start_identification = RM_Field_Record("Start identification",      1, self.BE, 0xAA)
        self.message_type         = RM_Field_Record("Message type",              1, self.BE, 0x54)
        self.message_length       = RM_Field_Record("Message length",            2, self.BE, 8)
        self.paket_number         = RM_Field_Record("Packet number",             2, self.BE, 0x0000)
        self.transmit_switch      = RM_Field_Record("Transmit switch (1 lsb)",   1, self.BE, transmit_switch)
        self.checksum             = RM_Field_Record("Checksum",                  1, self.BE, 0x00)


# Track Message
class RM_Track_Data (RM_Message):
    def __init__(self):
        super().__init__()
        self.track_lot         = RM_Field_Record("Track lot",                      2, self.BE, 0x0000)
        self.time_backup       = RM_Field_Record("backup (time)",                  1, self.BE, 0x00)
        self.time_hour         = RM_Field_Record("Hour",                           1, self.BE, 0x00)
        self.time_minutes      = RM_Field_Record("Minutes",                        1, self.BE, 0x00)
        self.time_seconds      = RM_Field_Record("Seconds",                        1, self.BE, 0x00)
        self.time_milliseconds = RM_Field_Record("Milliseconds",                   2, self.BE, 0x0000)
        self.normal_angle      = RM_Field_Record("Formation surface normal angle", 2, self.BE, 0x0000)
        self.reserved_16_18    = RM_Field_Record("Reserved 16~18",                 3, self.BE, 0x000000)
        pass


class RMM_Track_Message (RM_Message):
    def __init__(self, number_of_targets, tracks: [RM_Track_Data]):
        super().__init__()
        self.start_identification = RM_Field_Record("Start identification",      1, self.BE, 0xAA)
        self.message_type         = RM_Field_Record("Message type",              1, self.BE, 0x76)
        self.message_length       = RM_Field_Record("Message length",            2, self.BE, 10+32*number_of_targets)
        self.paket_number         = RM_Field_Record("Packet number",             2, self.BE, 0x0000)
        self.number_of_targets    = RM_Field_Record("Number of targets",         2, self.BE, number_of_targets)
        self.tracks = []
        for i in range(0, number_of_targets):
            self.tracks.append(RM_Track_Data())
        self.backups              = RM_Field_Record("backups",                   3, self.BE, 0)
        self.checksum             = RM_Field_Record("Checksum",                  1, self.BE, 0x00)
