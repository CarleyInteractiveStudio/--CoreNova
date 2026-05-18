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

CMD_GET_HW_CODE = b'\xFD'
CMD_ERASE = b'\x71'

class OukitelDefinitiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 FRP BYPASS - V2.2 (MODO AGRESIVO)")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="MTK BYPASS ENGINE - WP36", font=("Consolas", 18, "bold"), fg="#38bdf8", bg="#020617")
        self.header.pack(pady=15)

        self.status_label = tk.Label(root, text="ESTADO: LISTO", font=("Consolas", 12), fg="#4ade80", bg="#020617")
        self.status_label.pack()

        self.btn_run = tk.Button(root, text="INICIAR PROCESO", command=self.start_process,
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

    def handshake(self, ser):
        self.log("Enviando señales de sincronización (0xA0)...")
        ser.timeout = 0.001 # Muy rápido para no perder el timing
        start_time = time.time()

        while time.time() - start_time < 20:
            ser.write(b'\xA0')
            res = ser.read(1)

            if res:
                self.log(f"Respuesta recibida: {res.hex().upper()}")
                if res == b'\x5A':
                    self.log("¡Sincronización confirmada!")
                    # Secuencia extendida
                    for cmd in [b'\xA1', b'\xA2', b'\xA3', b'\xA4']:
                        ser.write(cmd)
                        time.sleep(0.01)
                        ser.read(1)
                    return True
                elif res in [b'\xF5', b'\x46', b'\xA0']:
                    self.log("Intentando forzar entrada...")
                    ser.write(b'\xA0')

            # Pequeño delay para no saturar el buffer
            time.sleep(0.001)
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.log_area.delete(1.0, tk.END)
        self.log("CONECTA AHORA: Apaga el cel y mantén VOL+ y VOL-.")

        port = None
        while self.running:
            port = self.find_mtk_port()
            if port: break
            time.sleep(0.1)

        if not port: return

        try:
            self.log(f"Puerto detectado: {port}. Abriendo...")
            with serial.Serial(port, 115200, timeout=1) as ser:
                if self.handshake(ser):
                    # Leer HW Code
                    ser.write(CMD_GET_HW_CODE)
                    ser.read(1) # skip cmd echo
                    ser.read(2) # skip status
                    hw_code = ser.read(2)
                    if hw_code:
                        self.log(f"Chip ID: MT{hw_code.hex().upper()}")

                    self.log("Intentando borrado de seguridad...")
                    ser.write(CMD_ERASE)
                    if ser.read(1) == CMD_ERASE:
                        ser.write(struct.pack(">I", FRP_START_ADDRESS))
                        ser.write(struct.pack(">I", FRP_START_ADDRESS + FRP_SIZE))
                        if ser.read(2) == b'\x00\x00':
                            self.log("¡EXITO TOTAL! FRP ELIMINADO.")
                            messagebox.showinfo("OK", "¡PROCESO COMPLETADO!")
                        else:
                            self.log("Error en la escritura final.")
                    else:
                        self.log("Seguridad activa. Usa SP Flash Tool ahora que el puerto está abierto.")
                else:
                    self.log("No se pudo sincronizar. Reintenta conectando el cable más rápido.")
        except Exception as e:
            self.log(f"ERROR: {str(e)}")

        self.running = False
        self.btn_run.config(state=tk.NORMAL)

    def start_process(self):
        if not self.running:
            threading.Thread(target=self.process_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelDefinitiveTool(root)
    root.mainloop()
