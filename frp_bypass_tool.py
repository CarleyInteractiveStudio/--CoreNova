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
        self.root.title("OUKITEL WP36 BYPASS - VERSION 4.0 (SINCRO 0x5F)")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="MTK BYPASS ENGINE v4.0", font=("Consolas", 18, "bold"), fg="#38bdf8", bg="#020617")
        self.header.pack(pady=15)

        self.status_label = tk.Label(root, text="ESTADO: LISTO", font=("Consolas", 12), fg="#4ade80", bg="#020617")
        self.status_label.pack()

        self.btn_run = tk.Button(root, text="INICIAR BYPASS v4.0", command=self.start_process,
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

    def handshake_v4(self, ser):
        self.log("Buscando sincronización v4.0 (SLA Bypass)...")
        ser.timeout = 0.01
        ser.reset_input_buffer()

        start_time = time.time()
        while time.time() - start_time < 30:
            ser.write(b'\xA0')
            res = ser.read(1)
            if res:
                # Si recibimos 0x5A o 0x5F (complemento de 0xA0)
                if res in [b'\x5A', b'\x5F']:
                    self.log(f"¡Sincronización Detectada: 0x{res.hex().upper()}!")
                    # Completar secuencia aceptando cualquier respuesta para no bloquearnos
                    for cmd in [b'\xA1', b'\xA2', b'\xA3', b'\xA4']:
                        ser.write(cmd)
                        ser.read(1)
                    return True
            time.sleep(0.005)
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log("INSTRUCCIONES:")
        self.log("1. Apaga el celular.")
        self.log("2. Mantén presionados VOL+ y VOL-.")
        self.log("3. Conecta el cable USB ahora.")

        last_port = None
        while self.running:
            port = self.find_mtk_port()
            if port and port != last_port:
                self.log(f"¡Dispositivo detectado en {port}!")
                last_port = port
                try:
                    # Usamos un timeout corto para la apertura inicial
                    with serial.Serial(port, 115200, timeout=0.1) as ser:
                        if self.handshake_v4(ser):
                            self.log("Bypass de seguridad activo. Intentando borrar FRP...")
                            ser.timeout = 1

                            # Comando de borrado (Format)
                            ser.write(b'\x71')
                            ack = ser.read(1)
                            if ack == b'\x71':
                                self.log("Comando de borrado aceptado.")
                                # Start address
                                ser.write(struct.pack(">I", FRP_START_ADDRESS))
                                # End address
                                ser.write(struct.pack(">I", FRP_START_ADDRESS + FRP_SIZE))

                                result = ser.read(2)
                                if result == b'\x00\x00':
                                    self.log("¡EXITO TOTAL! El bloqueo de Google ha sido eliminado.")
                                    self.status_label.config(text="ESTADO: ¡HACK COMPLETADO!", fg="#4ade80")
                                    messagebox.showinfo("EXITO", "Bloqueo FRP eliminado correctamente.")
                                    break
                                else:
                                    self.log(f"Fallo al borrar. Respuesta: {result.hex().upper()}")
                            else:
                                self.log("Error: El chip rechazó el borrado físico (SLA Activo).")
                                self.log("CONSEJO: Sin desconectar el celular, intenta usar SP Flash Tool.")
                        else:
                            self.log("No se pudo sincronizar. Reintenta la conexión.")
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
