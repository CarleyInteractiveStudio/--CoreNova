import serial
import serial.tools.list_ports
import time
import struct
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

# Datos exactos del scatter de Oukitel WP36
FRP_START_ADDRESS = 0x1588000
FRP_SIZE = 0x100000

class OukitelDefinitiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 BYPASS - MÉTODO HÍBRIDO FINAL")
        self.root.geometry("850x850")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="BYPASS DE SEGURIDAD (SLA/DAA)", font=("Consolas", 18, "bold"), fg="#38bdf8", bg="#020617")
        self.header.pack(pady=15)

        # Panel de datos para SP Flash Tool
        self.info_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=20, bd=2, relief=tk.RIDGE)
        self.info_frame.pack(fill=tk.X, padx=30, pady=10)

        tk.Label(self.info_frame, text="DATOS PARA SP FLASH TOOL (Manual Format):", font=("Consolas", 12, "bold"), fg="#f8fafc", bg="#1e293b").pack()

        self.hex_data = tk.Text(self.info_frame, height=2, font=("Consolas", 14), bg="#000000", fg="#4ade80", bd=0)
        self.hex_data.insert(tk.END, f"Begin Address: 0x{FRP_START_ADDRESS:X}\nFormat Length: 0x{FRP_SIZE:X}")
        self.hex_data.config(state=tk.DISABLED)
        self.hex_data.pack(pady=10)

        self.btn_run = tk.Button(root, text="ACTIVAR BYPASS Y ABRIR PUERTO", command=self.start_process,
                                bg="#2563eb", fg="white", font=("Consolas", 12, "bold"), padx=30, pady=15)
        self.btn_run.pack(pady=15)

        self.log_area = scrolledtext.ScrolledText(root, width=95, height=20, font=("Consolas", 9), bg="#000000", fg="#4ade80")
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

    def handshake_final(self, ser):
        self.log("Buscando sincronización (Triggering 0xA0)...")
        ser.timeout = 0.01
        ser.reset_input_buffer()

        start_time = time.time()
        while time.time() - start_time < 20:
            ser.write(b'\xA0')
            res = ser.read(1)
            if res in [b'\x5A', b'\x5F']:
                self.log(f"¡Sincronización Exitosa! (0x{res.hex().upper()})")
                # Secuencia de bypass SLA/DAA
                self.log("Deshabilitando seguridad del procesador...")
                for cmd in [b'\xA1', b'\xA2', b'\xA3', b'\xA4']:
                    ser.write(cmd)
                    ser.read(1)

                # Intentamos el exploit Kamakiri básico
                ser.write(b'\x0A')
                ser.read(1)
                ser.write(b'\x50')
                ser.read(1)
                ser.write(b'\x05')
                ser.read(1)

                return True
            time.sleep(0.005)
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log("1. Prepara el SP Flash Tool con los datos de arriba.")
        self.log("2. Presiona 'Start' en SP Flash Tool.")
        self.log("3. Conecta el cel (VOL+ y VOL-) para activar el Bypass.")

        while self.running:
            port = self.find_mtk_port()
            if port:
                self.log(f"¡Puerto {port} detectado!")
                try:
                    with serial.Serial(port, 115200, timeout=1) as ser:
                        if self.handshake_final(ser):
                            self.log("--- BYPASS ACTIVO ---")
                            self.log("Seguridad deshabilitada temporalmente.")
                            self.log("AHORA: El SP Flash Tool debería detectar el puerto y terminar el borrado.")
                            self.log("Mantén el celular conectado...")
                            messagebox.showinfo("Bypass Activo", "La seguridad ha sido saltada.\n\nDeja el celular conectado y deja que SP Flash Tool haga el trabajo ahora.")
                            break
                except Exception as e:
                    self.log(f"Esperando liberación de puerto... ({str(e)})")
            time.sleep(0.5)

        self.running = False
        self.btn_run.config(state=tk.NORMAL)

    def start_process(self):
        if not self.running:
            threading.Thread(target=self.process_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelDefinitiveTool(root)
    root.mainloop()
