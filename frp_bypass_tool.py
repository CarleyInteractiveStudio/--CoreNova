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
        self.root.title("OUKITEL WP36 BYPASS - FINAL V3.7 (PROTOCOLO HIBRIDO)")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="BYPASS FINAL v3.7 - OUKITEL WP36", font=("Consolas", 18, "bold"), fg="#facc15", bg="#020617")
        self.header.pack(pady=15)

        self.btn_run = tk.Button(root, text="INICIAR BYPASS FINAL v3.7", command=self.start_process,
                                bg="#ca8a04", fg="white", font=("Consolas", 12, "bold"), padx=30, pady=15)
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

    def handshake_hybrid(self, ser):
        self.log("Probando secuencia de Protocolo Híbrido (Revision B)...")
        ser.timeout = 0.1
        ser.reset_input_buffer()

        start_time = time.time()
        while time.time() - start_time < 20:
            # Primero intentamos el trigger estándar
            ser.write(b'\xA0')
            res = ser.read(1)

            if res == b'\x5A':
                self.log("Handshake Estándar (0x5A) Detectado.")
                # Sincro estándar
                for cmd in [b'\xA1', b'\xA2', b'\xA3', b'\xA4']:
                    ser.write(cmd)
                    ser.read(1)
                return True

            # Si no, intentamos la secuencia híbrida detectada
            # 0x0A -> 0xF5, 0x50 -> 0xAF, 0x05 -> 0xFA, 0x46 -> 0x46
            self.log("Intentando secuencia híbrida (0x0A -> 0xF5)...")
            ser.write(b'\x0A')
            if ser.read(1) == b'\xF5':
                self.log("Paso 1 OK (0xF5)")
                ser.write(b'\x50')
                if ser.read(1) == b'\xAF':
                    self.log("Paso 2 OK (0xAF)")
                    ser.write(b'\x05')
                    if ser.read(1) == b'\xFA':
                        self.log("Paso 3 OK (0xFA)")
                        ser.write(b'\x46')
                        if ser.read(1) == b'\x46':
                            self.log("¡HANDSHAKE HIBRIDO COMPLETADO!")
                            return True

            time.sleep(0.5)
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log("ESPERANDO DISPOSITIVO EN MODO BROM...")
        self.log("(Manten VOL+ y VOL- presionados y conecta el cable)")

        port = None
        while self.running:
            port = self.find_mtk_port()
            if port:
                self.log(f"Puerto detectado: {port}")
                try:
                    with serial.Serial(port, 115200, timeout=1) as ser:
                        if self.handshake_hybrid(ser):
                            self.log("Bypass Activo. Eliminando cuenta Google...")
                            # Comando de borrado directo
                            ser.write(b'\x71')
                            if ser.read(1) == b'\x71':
                                ser.write(struct.pack(">I", FRP_START_ADDRESS))
                                ser.write(struct.pack(">I", FRP_START_ADDRESS + FRP_SIZE))
                                if ser.read(2) == b'\x00\x00':
                                    self.log("¡LIBERACION EXITOSA! Bloqueo eliminado.")
                                    messagebox.showinfo("EXITO", "¡Cuenta eliminada!\n\nYa puedes encender el celular.")
                                    break
                                else:
                                    self.log("Fallo en la escritura. Seguridad SLA persistente.")
                            else:
                                self.log("Acceso denegado. Se requiere exploit adicional.")
                        else:
                            self.log("No se pudo sincronizar. Reintenta.")
                except Exception as e:
                    self.log(f"Error: {str(e)}")
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
