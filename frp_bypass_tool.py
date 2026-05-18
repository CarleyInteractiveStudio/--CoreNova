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
        self.root.title("OUKITEL WP36 BYPASS - DIAGNOSTICO V3.1")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="MODO DIAGNÓSTICO DE PUERTO", font=("Consolas", 18, "bold"), fg="#38bdf8", bg="#020617")
        self.header.pack(pady=15)

        self.btn_run = tk.Button(root, text="INICIAR ESCANEO", command=self.start_process,
                                bg="#2563eb", fg="white", font=("Consolas", 12, "bold"), padx=30, pady=15)
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

    def handshake_debug(self, ser):
        self.log(f"--- Iniciando Handshake en {ser.port} ---")
        ser.timeout = 0.05
        ser.reset_input_buffer()

        start_time = time.time()
        while time.time() - start_time < 15:
            ser.write(b'\xA0')
            res = ser.read(1)
            if res:
                self.log(f"Recibido: 0x{res.hex().upper()}")
                if res == b'\x5A':
                    self.log("¡SINCRO 0x5A DETECTADA!")
                    return True
                elif res == b'\xA0':
                    self.log("Eco detectado (el celular no está procesando comandos).")
            time.sleep(0.01)
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log("Buscando dispositivo...")

        last_port = None
        while self.running:
            port = self.find_mtk_port()
            if port and port != last_port:
                self.log(f"¡Dispositivo encontrado en {port}!")
                last_port = port
                try:
                    with serial.Serial(port, 115200, timeout=1) as ser:
                        if self.handshake_debug(ser):
                            self.log("Handshake exitoso. Continuando...")
                            # Intentar leer el ID del chip para confirmar
                            ser.write(b'\xFD')
                            id_res = ser.read(5)
                            self.log(f"Chip ID Data: {id_res.hex().upper()}")

                            # Intentar borrado
                            ser.write(b'\x71')
                            if ser.read(1) == b'\x71':
                                ser.write(struct.pack(">I", FRP_START_ADDRESS))
                                ser.write(struct.pack(">I", FRP_START_ADDRESS + FRP_SIZE))
                                if ser.read(2) == b'\x00\x00':
                                    self.log("¡BORRADO FRP COMPLETADO!")
                                    messagebox.showinfo("OK", "¡EXITO!")
                                    break
                            else:
                                self.log("Seguridad SLA activa. Acceso denegado.")
                        else:
                            self.log("No hubo respuesta 0x5A. ¿Zadig instalado?")
                except Exception as e:
                    self.log(f"Error al abrir puerto: {str(e)}")
            time.sleep(0.1)

        self.running = False
        self.btn_run.config(state=tk.NORMAL)

    def start_process(self):
        if not self.running:
            threading.Thread(target=self.process_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelDefinitiveTool(root)
    root.mainloop()
