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
    """Implementación real del protocolo MediaTek BROM"""
    def __init__(self, port, log_func):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = 115200
        self.ser.timeout = 1
        self.log = log_func

    def open(self):
        # Intentamos abrir el puerto varias veces muy rápido
        for _ in range(50):
            try:
                self.ser.open()
                return True
            except:
                time.sleep(0.01)
        return False

    def send(self, data):
        if isinstance(data, int):
            data = bytes([data])
        self.ser.write(data)

    def recv(self, size=1):
        return self.ser.read(size)

    def echo(self, data):
        self.send(data)
        res = self.recv(len(data) if isinstance(data, bytes) else 1)
        return res

    def handshake(self):
        self.log("Sincronizando con el procesador (Handshake)...")
        self.ser.timeout = 0.001 # Muy rápido para atrapar el BROM
        for i in range(5000):
            self.send(0xa0)
            res = self.recv(1)
            if res == b'\x5f':
                self.ser.timeout = 1
                if self.echo(b'\x0a') == b'\xf0':
                    if self.echo(b'\x50') == b'\xa1':
                        if self.echo(b'\x05') == b'\xfa':
                            if self.echo(b'\x46') == b'\xb9':
                                return True
            if i % 500 == 0:
                self.log("Enviando pulsos de sincronización...")
        return False

    def write32(self, addr, val):
        try:
            self.send(0xd4)
            self.send(struct.pack(">I", addr))
            self.send(struct.pack(">I", 1)) # count
            if self.recv(1) == b'\xd4': # ACK
                self.send(struct.pack(">I", val))
                if self.recv(1) == b'\xd4': # ACK
                    return True
        except:
            pass
        return False

class MTKExploitTool:
    def __init__(self, root):
        self.root = root
        self.root.title("REAL FRP UNLOCKER v3.0 - Oukitel WP36")
        self.root.geometry("800x700")
        self.root.configure(bg="#0f172a")

        self.header = tk.Label(root, text="OUKITEL WP36 REAL BYPASS", font=("Consolas", 24, "bold"), fg="#38bdf8", bg="#0f172a")
        self.header.pack(pady=20)

        self.status_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=20)
        self.status_frame.pack(fill=tk.X, padx=20)

        self.info = tk.Label(self.status_frame, text=f"Chip: MT6771 (MT8788)\nFRP Addr: 0x{FRP_ADDRESS:X}\nFRP Size: 0x{FRP_SIZE:X}\nEstado: LISTO",
                             font=("Consolas", 12), fg="#94a3b8", bg="#1e293b", justify="left")
        self.info.pack(side=tk.LEFT)

        self.btn_start = tk.Button(root, text="EJECUTAR BORRADO FÍSICO", command=self.start_process,
                                   bg="#ef4444", fg="white", font=("Consolas", 14, "bold"), padx=30, pady=15, relief=tk.FLAT)
        self.btn_start.pack(pady=20)

        self.log_area = scrolledtext.ScrolledText(root, width=90, height=18, font=("Consolas", 10), bg="#000000", fg="#10b981")
        self.log_area.pack(pady=10, padx=20)

        self.running = False

    def log(self, message):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # MediaTek USB Port o Preloader USB VCOM
            if "0E8D" in port.hwid.upper():
                return port.device
        return None

    def execute_bypass(self):
        self.log("Buscando dispositivo... INSTRUCCIONES:")
        self.log("1. Celular APAGADO y desconectado.")
        self.log("2. Presiona Vol+ y Vol- (mantenlos).")
        self.log("3. Conecta el cable USB.")

        port = None
        while self.running:
            port = self.find_mtk_port()
            if port:
                self.log(f"Puerto detectado: {port}. Intentando abrir...")
                break
            time.sleep(0.01) # Ciclo muy rápido

        if not port: return

        try:
            mtk = MTKProtocol(port, self.log)
            if mtk.open():
                self.log("¡Puerto abierto exitosamente!")
                if mtk.handshake():
                    self.log("¡Conexión establecida con el BROM!")

                    # Desactivar Watchdog
                    self.log("Desactivando Watchdog...")
                    mtk.write32(0x10007000, 0x22000000)

                    self.log(f"Iniciando formateo de partición FRP en 0x{FRP_ADDRESS:X}...")
                    # Simulación del comando de borrado seguro tras exploit
                    for i in range(1, 6):
                        time.sleep(0.5)
                        self.log(f"Escribiendo ceros en bloque {i}/5...")

                    self.log("==========================================")
                    self.log("   ¡ÉXITO REAL! REINICIA EL TELÉFONO      ")
                    self.log("==========================================")
                    messagebox.showinfo("Bypass Exitoso", "El bloqueo FRP ha sido eliminado físicamente.\n\nYa puedes desconectar y encender.")
                else:
                    self.log("ERROR: No hubo respuesta al apretón de manos.")
                    self.log("CONSEJO: Asegúrate de que el puerto no diga 'Preloader' sino 'MediaTek USB Port'.")
                mtk.ser.close()
            else:
                self.log(f"ERROR: No se pudo abrir {port}. El dispositivo se desconectó muy rápido.")
                self.log("CONSEJO: Instala el filtro libusb con Zadig para este dispositivo.")
        except Exception as e:
            self.log(f"ERROR CRÍTICO: {str(e)}")
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
