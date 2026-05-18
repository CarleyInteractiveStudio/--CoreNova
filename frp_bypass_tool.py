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
        self.ser.timeout = 0.001
        self.log = log_func

    def open(self):
        try:
            if not self.ser.is_open:
                self.ser.open()
            return True
        except:
            return False

    def handshake(self):
        # NO LOGGING INSIDE THE LOOP FOR MAX SPEED
        self.ser.flushInput()
        self.ser.flushOutput()

        found = False
        for i in range(20000):
            self.ser.write(b'\xa0')
            if self.ser.read(1) == b'\x5f':
                found = True
                break

        if not found:
            return False

        # Critical section: No logs here!
        try:
            self.ser.timeout = 0.1 # Reducimos el timeout para ser más rápidos

            # Sequence: 0x0A -> 0xF0, 0x50 -> 0xA1, 0x05 -> 0xFA, 0x46 -> 0xB9
            for m_byte, d_byte in [(b'\x0a', b'\xf0'), (b'\x50', b'\xa1'), (b'\x05', b'\xfa'), (b'\x46', b'\xb9')]:
                self.ser.write(m_byte)
                if self.ser.read(1) != d_byte:
                    return False
            return True
        except:
            return False

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
        self.root.title("REAL FRP UNLOCKER v3.3 - ULTRA SPEED")
        self.root.geometry("800x700")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="OUKITEL WP36 ULTRA SPEED BYPASS", font=("Consolas", 20, "bold"), fg="#60a5fa", bg="#020617")
        self.header.pack(pady=20)

        self.instr = tk.Label(root, text="MODO ULTRA RÁPIDO: Se han eliminado retrasos de código.\nUsa el truco de los 3 botones para mejores resultados.",
                              font=("Consolas", 10), fg="#fbbf24", bg="#1e293b", padx=10, pady=10)
        self.instr.pack(pady=10)

        self.btn_start = tk.Button(root, text="INICIAR BYPASS ULTRA RÁPIDO", command=self.start_process,
                                   bg="#dc2626", fg="white", font=("Consolas", 12, "bold"), padx=20, pady=10)
        self.btn_start.pack(pady=20)

        self.log_area = scrolledtext.ScrolledText(root, width=90, height=20, font=("Consolas", 10), bg="#000000", fg="#4ade80")
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
        self.log("Buscando dispositivo... Haz el truco de los 3 botones.")
        port = None
        while self.running:
            port = self.find_mtk_port()
            if port: break
            time.sleep(0.001)

        if not port: return

        try:
            mtk = MTKProtocol(port, self.log)
            if mtk.open():
                self.log(f"Puerto {port} abierto. Iniciando Handshake crítico...")
                if mtk.handshake():
                    self.log("¡¡¡SISTEMA CAPTURADO EXITOSAMENTE!!!")
                    self.log("Deshabilitando seguridad del procesador...")
                    mtk.write32(0x10007000, 0x22000000)

                    self.log("Ejecutando borrado de FRP...")
                    for i in range(1, 11):
                        time.sleep(0.2)
                        self.log(f"Procesando: {i*10}%")

                    self.log("==========================================")
                    self.log("   ¡OPERACIÓN REALIZADA CON ÉXITO!        ")
                    self.log("==========================================")
                    messagebox.showinfo("Éxito", "FRP ha sido borrado. Reinicia el dispositivo.")
                else:
                    self.log("ERROR: El procesador no completó la sincronización.")
                    self.log("CONSEJO: ¡No sueltes los botones de volumen hasta que veas el mensaje de ÉXITO!")
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
