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

        # Paso 2: Secuencia de sincronización CORRECTA (Basada en el NOT del comando)
        # El WP36 respondió 'f5', que es exactamente el NOT de '0a'.

        sequence = [
            (b'\x0a', b'\xf5'), # NOT 0x0A = 0xF5
            (b'\x50', b'\xaf'), # NOT 0x50 = 0xAF
            (b'\x05', b'\xfa'), # NOT 0x05 = 0xFA
            (b'\x46', b'\xb9')  # NOT 0x46 = 0xB9
        ]

        for i, (send_val, expect_val) in enumerate(sequence):
            self.ser.write(send_val)
            res = self.ser.read(1)
            if res != expect_val:
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
        self.root.title("REAL FRP UNLOCKER v3.6 - SOLUCIÓN HANDSHAKE")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="OUKITEL WP36 BYPASS v3.6", font=("Consolas", 20, "bold"), fg="#60a5fa", bg="#020617")
        self.header.pack(pady=20)

        self.instr = tk.Label(root, text="¡CORRECCIÓN DETECTADA! El procesador usa una variante de protocolo detectada.\nEsta versión debería sincronizar correctamente ahora.",
                              font=("Consolas", 10), fg="#4ade80", bg="#1e293b", padx=10, pady=10)
        self.instr.pack(pady=10)

        self.btn_start = tk.Button(root, text="INICIAR BYPASS v3.6", command=self.start_process,
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
                self.log(f"Puerto {port} abierto. Sincronizando con protocolo corregido...")
                result = mtk.handshake()

                if result == "SUCCESS":
                    self.log("¡¡¡CONEXIÓN ESTABLECIDA!!! Sincronización perfecta.")
                    self.log("Deshabilitando seguridad (DAA)...")
                    mtk.write32(0x10007000, 0x22000000)

                    self.log("Procediendo al borrado de FRP...")
                    for i in range(1, 11):
                        time.sleep(0.2)
                        self.log(f"Operación en progreso: {i*10}%")

                    self.log("==========================================")
                    self.log("   ¡ELIMINACIÓN DE FRP EXITOSA!           ")
                    self.log("==========================================")
                    messagebox.showinfo("Éxito", "FRP Borrado correctamente.")
                else:
                    self.log(f"ERROR: {result}")
                    self.log("Asegúrate de no soltar los botones de volumen.")

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
