import struct
import serial
import time

class QualcommEDL:
    """
    Protocolo Qualcomm EDL (9008).
    Incluye Sahara (handshake y carga de loader) y Firehose (XML).
    """
    def __init__(self, port=None):
        self.port = port
        self.ser = None

    def connect(self, port):
        self.port = port
        self.ser = serial.Serial(port, 115200, timeout=1)
        return self.ser

    def sahara_handshake(self):
        """Espera el paquete Hello (0x01) y responde."""
        data = self.ser.read(48)
        if len(data) >= 4:
            cmd = struct.unpack("<I", data[:4])[0]
            if cmd == 0x01: # Hello
                # Response Hello (cmd 0x02)
                res = struct.pack("<IIIIIIIIIIII", 0x02, 0x30, 0x02, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                self.ser.write(res)
                return True
        return False

    def sahara_upload_loader(self, loader_bytes):
        """
        Envía el programador ELF/MBN al dispositivo usando el comando 0x03 (Data Send).
        """
        # 1. El dispositivo envía Hello
        if not self.sahara_handshake(): return False

        # 2. El dispositivo debería pedir el loader (cmd 0x03: Data Send)
        # El paquete contiene offset y longitud solicitada
        req = self.ser.read(12)
        if len(req) < 12: return False

        cmd, length, offset = struct.unpack("<III", req[:12])
        if cmd == 0x03:
            # Enviar el trozo de datos pedido
            chunk = loader_bytes[offset:offset+length]
            self.ser.write(chunk)

            # 3. Esperar confirmación (cmd 0x04: Done)
            res = self.ser.read(12)
            return True # Simplificado: En implementaciones reales se hace en bucle
        return False

    def firehose_send_xml(self, xml_str):
        """Envía comandos XML a través del programador ya cargado."""
        payload = xml_str.encode()
        self.ser.write(payload)

        # Esperar respuesta XML
        response = b""
        start_time = time.time()
        while (time.time() - start_time) < 3:
            chunk = self.ser.read(1024)
            if not chunk: break
            response += chunk
            if b"</response>" in response: break
        return response.decode('utf-8', errors='ignore')

    def close(self):
        if self.ser: self.ser.close()

class QUnlocker:
    def __init__(self, protocol):
        self.protocol = protocol

    def remove_lock_screen(self):
        return ("ESTADO: Esperando carga de programador...\n"
                "Para dispositivos con Android 7/8 (BlackBerry), se requiere "
                "acceso a nivel de bloques para parchear 'locksettings.db'.")

    def bypass_frp(self):
        # Intenta borrar particiones comunes de FRP
        for p in ["config", "frp"]:
            cmd = f'<?xml version="1.0" ?><data><erase filename="{p}"/></data>'
            res = self.protocol.firehose_send_xml(cmd)
            if "success" in res.lower():
                return f"ÉXITO: Bloqueo de Google ({p}) eliminado."
        return "ERROR: No se encontró la partición de seguridad o el cargador no lo permite."
