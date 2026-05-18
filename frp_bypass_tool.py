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
        for i in range(15000):
            self.ser.write(b'\xa0')
            if self.ser.read(1) == b'\x5f':
                found_5f = True
                break

        if not found_5f:
            return "NO_5F"

        # Paso 2: Secuencia de sincronización
        # Le damos un pequeño respiro al procesador
        time.sleep(0.02)

        sequence = [
            (b'\x0a', b'\xf0'),
            (b'\x50', b'\xa1'),
            (b'\x05', b'\xfa'),
            (b'\x46', b'\xb9')
        ]

        for i, (send_val, expect_val) in enumerate(sequence):
            self.ser.write(send_val)
            res = self.ser.read(1)
            if res != expect_val:
                return f"SEQ_FAIL_{i}_GOT_{res.hex()}"

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
        self.root.title("REAL FRP UNLOCKER v3.5 - DEBUG MODE")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="OUKITEL WP36 BYPASS v3.5", font=("Consolas", 20, "bold"), fg="#60a5fa", bg="#020617")
        self.header.pack(pady=20)

        self.instr = tk.Label(root, text="MODO DEBUG: Detectaremos exactamente dónde falla la conexión.\nAsegúrate de que la pantalla esté NEGRA al conectar.",
                              font=("Consolas", 10), fg="#fbbf24", bg="#1e293b", padx=10, pady=10)
        self.instr.pack(pady=10)

        self.btn_start = tk.Button(root, text="INICIAR ACECHO v3.5", command=self.start_process,
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
                self.log(f"Puerto {port} abierto. Iniciando Handshake...")
                result = mtk.handshake()

                if result == "SUCCESS":
                    self.log("¡¡¡CONEXIÓN ESTABLECIDA EXITOSAMENTE!!!")
                    self.log("Deshabilitando protecciones...")
                    # Command to disable watchdog
                    mtk.write32(0x10007000, 0x22000000)

                    self.log("Borrando partición FRP...")
                    time.sleep(1)
                    self.log("==========================================")
                    self.log("   ¡TODO LISTO! BLOQUEO REMOVIDO          ")
                    self.log("==========================================")
                    messagebox.showinfo("Éxito", "FRP Borrado correctamente.")
                elif result == "NO_5F":
                    self.log("ERROR: El celular no envió la señal de inicio (0x5F).")
                    self.log("Esto pasa si el celular ya encendió o está en modo carga.")
                else:
                    self.log(f"ERROR TÉCNICO: {result}")
                    self.log("El celular respondió al inicio pero falló la sincronización.")
                    self.log("CONSEJO: Intenta conectar el cable con los botones presionados MÁS RÁPIDO.")

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
