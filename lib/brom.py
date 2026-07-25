import serial
import struct
import time

class MTKProtocol:
    def __init__(self, port=None):
        self.port = port
        self.ser = None

    def connect(self, port):
        self.port = port
        self.ser = serial.Serial(port, 115200, timeout=0.1)
        return self.ser

    def handshake(self):
        self.ser.reset_input_buffer()
        for _ in range(500):
            self.ser.write(b'\xA0')
            res = self.ser.read(1)
            if res in [b'\x5A', b'\x5F', b'\xA5']:
                self.ser.write(b'\xA0') # Confirm
                self.ser.read(1)
                return True
        return False

    def get_hw_code(self):
        self.ser.write(b'\xFD') # READ_VERSION
        res = self.ser.read(4)
        if len(res) == 4:
            return struct.unpack(">I", res)[0]
        return None

    def format_partition(self, address, size):
        self.ser.write(b'\xD4')
        if self.ser.read(1) == b'\xD4':
            self.ser.write(struct.pack(">I", address))
            self.ser.write(struct.pack(">I", size))
            res = self.ser.read(2)
            return res == b'\x00\x00'
        return False

    def read_memory(self, address, size):
        self.ser.write(b'\xD2') # READ_DATA
        if self.ser.read(1) == b'\xD2':
            self.ser.write(struct.pack(">I", address))
            self.ser.write(struct.pack(">I", size))
            self.ser.read(2) # Ack/Status
            data = self.ser.read(size)
            return data
        return None

    def write_memory(self, address, data):
        size = len(data)
        self.ser.write(b'\xD1') # WRITE_DATA
        if self.ser.read(1) == b'\xD1':
            self.ser.write(struct.pack(">I", address))
            self.ser.write(struct.pack(">I", size))
            self.ser.read(2) # Ack
            self.ser.write(data)
            res = self.ser.read(2)
            return res == b'\x00\x00'
        return False

    def send_payload(self, payload_dict):
        """Aplica un payload (diccionario de dirección: valor)"""
        success = True
        for addr, val in payload_dict.items():
            if not self.write_memory(addr, struct.pack(">I", val)):
                success = False
        return success

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
