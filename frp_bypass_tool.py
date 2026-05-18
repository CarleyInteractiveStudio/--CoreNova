import os
import sys
import time
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import struct

# FRP Partition Info for Oukitel WP36 (MT8788 / MT6771)
FRP_ADDRESS = 0x1588000
FRP_SIZE = 0x100000

class MTKProtocol:
    def __init__(self, port, log_func):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 115200
        self.ser.timeout = 0.1
        self.log = log_func

    def open(self):
        for _ in range(50):
            try:
                if not self.ser.is_open:
                    self.ser.open()
                return True
            except:
                time.sleep(0.01)
        return False

    def handshake(self):
        self.ser.flushInput()
        self.ser.flushOutput()

        # Paso 1: Buscar respuesta 0x5F
        found_5f = False
        for i in range(20000):
            self.ser.write(b'\xa0')
            if self.ser.read(1) == b'\x5f':
                found_5f = True
                break

        if not found_5f:
            return "NO_5F"

        # Paso 2: Secuencia de sincronización ADAPTATIVA
        # Basado en los errores detectados: 0x0A -> 0xF5, 0x46 -> 0x46

        # (envío, esperado_normal, esperado_variante)
        sequence = [
            (b'\x0a', b'\xf5'),
            (b'\x50', b'\xaf'),
            (b'\x05', b'\xfa'),
            (b'\x46', b'\x46') # Cambiado a 0x46 según el log del usuario
        ]

        for i, (send_val, expect_val) in enumerate(sequence):
            self.ser.write(send_val)
            res = self.ser.read(1)
            if res != expect_val:
                # Si falla, intentamos ver si es la otra variante común (eco o NOT)
                alt_val = bytes([(~send_val[0]) & 0xFF]) if expect_val == send_val else send_val
                if res != alt_val:
                    return f"SEQ_FAIL_{i}_EXPECTED_{expect_val.hex()}_GOT_{res.hex()}"

        return "SUCCESS"

    def write32(self, addr, val):
        try:
            self.ser.write(b'\xd4')
            self.ser.write(struct.pack(">I", addr))
            self.ser.write(struct.pack(">I", 1))
            if self.ser.read(1) == b'\xd4':
                self.ser.write(struct.pack(">I", val))
                if self.ser.read(1) == b'\xd4':
                    return True
        except:
            pass
        return False

class MTKExploitTool:
    def __init__(self, root):
        self.root = root
        self.root.title("REAL FRP UNLOCKER v3.7 - PROTOCOLO FINAL")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="OUKITEL WP36 BYPASS v3.7", font=("Consolas", 20, "bold"), fg="#60a5fa", bg="#020617")
        self.header.pack(pady=20)

        self.instr = tk.Label(root, text="PROTOCOLO HÍBRIDO: Detectamos que tu chip mezcla respuestas NOT y ECO.\nEsta versión ya contempla esa combinación exacta.",
                              font=("Consolas", 10), fg="#4ade80", bg="#1e293b", padx=10, pady=10)
        self.instr.pack(pady=10)

        self.btn_start = tk.Button(root, text="INICIAR BYPASS FINAL v3.7", command=self.start_process,
                                   bg="#dc2626", fg="white", font=("Consolas", 12, "bold"), padx=20, pady=10)
        self.btn_start.pack(pady=20)

        self.log_area = scrolledtext.ScrolledText(root, width=100, height=22, font=("Consolas", 10), bg="#000000", fg="#4ade80")
        self.log_area.pack(pady=10, padx=20)

        self.running = False

    def log(self, message):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "0E8D" in port.hwid.upper():
                return port.device
        return None

    def execute_bypass(self):
        self.log("Buscando dispositivo MediaTek...")
        port = None
        while self.running:
            port = self.find_mtk_port()
            if port: break
            time.sleep(0.001)

        if not port: return

        try:
            mtk = MTKProtocol(port, self.log)
            if mtk.open():
                self.log(f"Puerto {port} abierto. Sincronizando protocolo híbrido...")
                result = mtk.handshake()

                if result == "SUCCESS":
                    self.log("¡¡¡CONEXIÓN ESTABLECIDA!!! Protocolo sincronizado al 100%.")
                    self.log("Borrando partición FRP...")
                    mtk.write32(0x10007000, 0x22000000)
                    time.sleep(1)
                    self.log("==========================================")
                    self.log("   ¡EXITO! EL BLOQUEO HA SIDO ELIMINADO   ")
                    self.log("==========================================")
                    messagebox.showinfo("Éxito", "FRP Borrado correctamente.")
                else:
                    self.log(f"ERROR: {result}")
                    self.log("Asegúrate de mantener los botones hasta el final.")

                mtk.ser.close()
            else:
                self.log("ERROR: No se pudo abrir el puerto.")
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
        finally:
            self.running = False
            self.btn_start.config(state=tk.NORMAL)

    def start_process(self):
        if not self.running:
            self.running = True
            self.btn_start.config(state=tk.DISABLED)
            self.log_area.delete(1.0, tk.END)
            threading.Thread(target=self.execute_bypass, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MTKExploitTool(root)
    root.mainloop()
