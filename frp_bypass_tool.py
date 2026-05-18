import serial
import serial.tools.list_ports
import time
import struct
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

# Oukitel WP36 (MT8788 / MT6771)
FRP_START_ADDRESS = 0x1588000
FRP_SIZE = 0x100000

class OukitelDefinitiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 BYPASS - ULTRA BYPASS V3.0")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="MTK ULTRA BYPASS - SIN TIMEOUTS", font=("Consolas", 18, "bold"), fg="#f43f5e", bg="#020617")
        self.header.pack(pady=15)

        self.btn_run = tk.Button(root, text="ACTIVAR MODO ULTRA (RAFAGA)", command=self.start_process,
                                bg="#e11d48", fg="white", font=("Consolas", 12, "bold"), padx=30, pady=15)
        self.btn_run.pack(pady=15)

        self.log_area = scrolledtext.ScrolledText(root, width=95, height=25, font=("Consolas", 9), bg="#000000", fg="#4ade80")
        self.log_area.pack(pady=10, padx=20)

        self.running = False

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        for p in serial.tools.list_ports.comports():
            if "0E8D" in p.hwid.upper():
                return p.device
        return None

    def handshake(self, ser):
        self.log("ENVIANDO RÁFAGA DE SINCRONIZACIÓN...")
        ser.timeout = 0.001 # El secreto está aquí
        ser.reset_input_buffer()

        # Enviamos ráfagas de 0xA0
        for _ in range(500):
            ser.write(b'\xA0')
            res = ser.read(1)
            if res == b'\x5A':
                self.log("¡HANDSHAKE ATRAPADO!")
                # Completar handshake
                for cmd in [b'\xA1', b'\xA2', b'\xA3', b'\xA4']:
                    ser.write(cmd)
                    ser.read(1)
                return True
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log("LISTO PARA ATRAPAR EL PUERTO...")
        self.log("Paso 1: Ten el cel desconectado y APAGADO.")
        self.log("Paso 2: Presiona VOL+ y VOL- sin soltar.")
        self.log("Paso 3: Conecta el cable USB.")

        port = None
        while self.running:
            port = self.find_mtk_port()
            if port:
                self.log(f"¡PUERTO DETECTADO! {port}")
                try:
                    # Apertura ultra-rápida
                    ser = serial.Serial(port, 115200, timeout=0.001)
                    if self.handshake(ser):
                        self.log("Bypass activo. Intentando borrar bloqueo...")
                        ser.timeout = 1
                        ser.write(b'\x71')
                        if ser.read(1) == b'\x71':
                            ser.write(struct.pack(">I", FRP_START_ADDRESS))
                            ser.write(struct.pack(">I", FRP_START_ADDRESS + FRP_SIZE))
                            if ser.read(2) == b'\x00\x00':
                                self.log("¡EXITO TOTAL!")
                                messagebox.showinfo("COMPLETO", "Bloqueo eliminado.")
                            else: self.log("Error de escritura.")
                        else:
                            self.log("SEGURIDAD ACTIVA. USA SP FLASH TOOL AHORA.")
                        ser.close()
                        break
                    ser.close()
                except:
                    pass
            time.sleep(0.01)

        self.running = False
        self.btn_run.config(state=tk.NORMAL)

    def start_process(self):
        if not self.running:
            threading.Thread(target=self.process_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelDefinitiveTool(root)
    root.mainloop()
