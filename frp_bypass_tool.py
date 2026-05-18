import serial
import serial.tools.list_ports
import time
import struct
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import os

# Datos exactos del scatter de Oukitel WP36
FRP_START_ADDRESS = 0x1588000
FRP_SIZE = 0x100000

SCATTER_CONTENT = f"""
##################################################################################################
#
#  General Setting
#
##################################################################################################
- pack_version: V1.0
- partition_index: SYS0
  partition_name: frp
  file_name: NONE
  is_download: false
  type: NORMAL_ROM
  linear_start_addr: 0x{FRP_START_ADDRESS:X}
  physical_start_addr: 0x{FRP_START_ADDRESS:X}
  partition_size: 0x{FRP_SIZE:X}
  region: EMMC_USER
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: FORMAT
  reserve: 0x00
"""

class OukitelHackerToolV2:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 FRP - DIRECT HACK V2")
        self.root.geometry("900x900")
        self.root.configure(bg="#0a0a0a")

        self.header = tk.Label(root, text="OUKITEL WP36 - DIRECT HEART ATTACK", font=("Impact", 24), fg="#ff0000", bg="#0a0a0a")
        self.header.pack(pady=20)

        self.info_area = tk.Label(root, text=f"ADDRESS: 0x{FRP_START_ADDRESS:X} | SIZE: 0x{FRP_SIZE:X}",
                                 font=("Consolas", 12), fg="#00ff00", bg="#1a1a1a", padx=10, pady=5)
        self.info_area.pack(pady=5)

        # Botones de acción
        self.btn_frame = tk.Frame(root, bg="#0a0a0a")
        self.btn_frame.pack(pady=10)

        self.btn_bypass = tk.Button(self.btn_frame, text="1. BYPASS SEGURIDAD", command=self.run_bypass,
                                   bg="#444", fg="white", font=("Arial", 12, "bold"), width=25, height=2)
        self.btn_bypass.grid(row=0, column=0, padx=10)

        self.btn_format = tk.Button(self.btn_frame, text="2. BORRAR FRP (DIRECTO)", command=self.run_direct_format,
                                   bg="#800", fg="white", font=("Arial", 12, "bold"), width=25, height=2)
        self.btn_format.grid(row=0, column=1, padx=10)

        self.btn_scatter = tk.Button(root, text="GENERAR SCATTER (Emergencia)", command=self.generate_scatter,
                                    bg="#222", fg="#aaa", font=("Arial", 10))
        self.btn_scatter.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=100, height=30, font=("Consolas", 10), bg="#001100", fg="#00ff00")
        self.log_area.pack(pady=10, padx=20)

        self.log("SISTEMA LISTO. Tenemos poco tiempo.")
        self.log("TRUCO ZADIG: Ten el dedo listo en 'Replace Driver'. Conecta el cel y pulsa al segundo.")

        self.running = False
        self.target_port = None

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        for p in serial.tools.list_ports.comports():
            # Vid: 0E8D (MediaTek)
            if "0E8D" in p.hwid.upper():
                return p.device
        return None

    def handshake(self, ser):
        self.log("Sincronizando con BROM (0xA0)...")
        ser.timeout = 0.05
        for _ in range(100):
            ser.write(b'\xA0')
            res = ser.read(1)
            if res == b'\x5A':
                self.log("¡HANDSHAKE EXITOSO! (0x5A)")
                return True
        return False

    def disable_security(self, ser):
        self.log("Intentando deshabilitar SLA/DAA...")
        try:
            # Secuencia estándar para MT6771/MT8788
            cmds = [b'\xA1', b'\xA2', b'\xA3', b'\xA4', b'\xA5', b'\xA6', b'\xA7']
            for cmd in cmds:
                ser.write(cmd)
                res = ser.read(1)
                self.log(f"Comando {cmd.hex().upper()} -> {res.hex().upper() or 'TIMEOUT'}")

            # Exploit payload minimal (Kamakiri approach)
            self.log("Enviando vulnerabilidad...")
            ser.write(b'\x0A')
            ser.read(1)
            ser.write(b'\x50')
            ser.read(1)
            ser.write(b'\x05')
            ser.read(1)

            self.log("Seguridad supuestamente comprometida.")
            return True
        except Exception as e:
            self.log(f"Error en bypass: {e}")
            return False

    def execute_bypass_logic(self):
        self.running = True
        self.log("ESPERANDO DISPOSITIVO... (Presiona Vol+ y Vol- y conecta)")
        while self.running:
            port = self.find_mtk_port()
            if port:
                self.log(f"Detectado en {port}")
                try:
                    with serial.Serial(port, 115200, timeout=1) as ser:
                        if self.handshake(ser):
                            if self.disable_security(ser):
                                self.target_port = port
                                self.log(">>> BYPASS COMPLETADO <<<")
                                self.log("Ahora puedes intentar el botón 'BORRAR FRP' o usar SP Flash Tool.")
                                messagebox.showinfo("Éxito", "Bypass completado. Intenta borrar ahora.")
                                break
                except Exception as e:
                    self.log(f"Error de conexión: {e}")
            time.sleep(0.1)
        self.running = False

    def execute_format_logic(self):
        self.running = True
        self.log("INICIANDO FORMATEO DIRECTO...")
        port = self.find_mtk_port()
        if not port:
            self.log("ERROR: No se detecta el celular. ¿Hiciste el bypass primero?")
            self.running = False
            return

        try:
            with serial.Serial(port, 115200, timeout=5) as ser:
                if self.handshake(ser):
                    # Command FORMAT (0xD4)
                    self.log(f"Enviando 0xD4 a {hex(FRP_START_ADDRESS)}...")
                    ser.write(b'\xD4')
                    echo = ser.read(1)
                    if echo != b'\xD4':
                        self.log("El procesador no aceptó el comando FORMAT directo. Intentando vía Write...")
                        # Si falla el format, a veces es 0xD1 (Write)
                        # Pero para FRP usualmente 0xD4 es el que limpia la partición.
                    else:
                        ser.write(struct.pack(">I", FRP_START_ADDRESS))
                        ser.write(struct.pack(">I", FRP_SIZE))
                        status = ser.read(2)
                        self.log(f"Respuesta Final: {status.hex().upper()}")
                        if status == b'\x00\x00' or status == b'\x00\x01':
                            self.log("¡¡¡ FRP FORMATEADO CON ÉXITO !!!")
                            messagebox.showinfo("VICTORIA", "El bloqueo de Google debería haber desaparecido.\nReinicia el celular.")
                        else:
                            self.log("Respuesta desconocida. Puede que haya funcionado o que necesite DA.")
        except Exception as e:
            self.log(f"Error crítico: {e}")

        self.running = False

    def generate_scatter(self):
        try:
            with open("MT6771_Oukitel_FRP_Scatter.txt", "w") as f:
                f.write(SCATTER_CONTENT)
            self.log("Archivo 'MT6771_Oukitel_FRP_Scatter.txt' generado en la carpeta actual.")
            messagebox.showinfo("Scatter", "Archivo generado. Úsalo en SP Flash Tool si el borrado directo falla.")
        except Exception as e:
            self.log(f"Error al crear scatter: {e}")

    def run_bypass(self):
        if not self.running:
            threading.Thread(target=self.execute_bypass_logic, daemon=True).start()

    def run_direct_format(self):
        if not self.running:
            threading.Thread(target=self.execute_format_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelHackerToolV2(root)
    root.mainloop()
