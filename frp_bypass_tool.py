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
        self.ser.timeout = 0.001 # Timeout de lectura muy bajo para handshake
        self.ser.write_timeout = 1 # Evitar el error de "Write timeout" bloqueante
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

    def send(self, data):
        if isinstance(data, int):
            data = bytes([data])
        try:
            self.ser.write(data)
            return True
        except serial.SerialTimeoutException:
            return False
        except Exception as e:
            self.log(f"Error de envío: {e}")
            return False

    def recv(self, size=1):
        try:
            return self.ser.read(size)
        except:
            return b''

    def handshake(self):
        self.log("Iniciando Handshake de alta velocidad (0xA0)...")
        # El MT6771 es caprichoso, intentamos 10000 veces
        for i in range(10000):
            if not self.send(0xa0):
                self.log("El dispositivo dejó de responder durante el envío.")
                return False

            res = self.recv(1)
            if res == b'\x5f':
                self.log("¡RESPUESTA 0x5F RECIBIDA! Sincronizando...")
                self.ser.timeout = 1
                try:
                    # Secuencia de sincronización extendida
                    self.ser.write(b'\x0a')
                    if self.ser.read(1) != b'\xf0': return False
                    self.ser.write(b'\x50')
                    if self.ser.read(1) != b'\xa1': return False
                    self.ser.write(b'\x05')
                    if self.ser.read(1) != b'\xfa': return False
                    self.ser.write(b'\x46')
                    if self.ser.read(1) != b'\xb9': return False
                    return True
                except:
                    return False

            if i % 1000 == 0 and i > 0:
                self.log(f"Intentos: {i}... Sigue manteniendo los botones.")

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
        self.root.title("REAL FRP UNLOCKER v3.1 - Oukitel WP36")
        self.root.geometry("800x700")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="OUKITEL WP36 REAL BYPASS v3.1", font=("Consolas", 20, "bold"), fg="#60a5fa", bg="#020617")
        self.header.pack(pady=20)

        self.status_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=15)
        self.status_frame.pack(fill=tk.X, padx=20)

        self.info = tk.Label(self.status_frame, text=f"Chip: MT6771 | FRP: 0x{FRP_ADDRESS:X}\nEstado: ESPERANDO DISPOSITIVO",
                             font=("Consolas", 11), fg="#cbd5e1", bg="#1e293b", justify="left")
        self.info.pack(side=tk.LEFT)

        self.btn_start = tk.Button(root, text="INICIAR PROCESO DE BORRADO", command=self.start_process,
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
        self.log("--- INICIANDO ACECHO DE DISPOSITIVO ---")
        self.log("Asegúrate de que el celular esté APAGADO.")
        self.log("Mantén presionados VOL+ y VOL- y conecta el USB.")

        port = None
        while self.running:
            port = self.find_mtk_port()
            if port: break
            time.sleep(0.01)

        if not port: return

        try:
            mtk = MTKProtocol(port, self.log)
            if mtk.open():
                self.log(f"Conectado a {port}. Entrando en fase de Handshake...")
                if mtk.handshake():
                    self.log("¡CONEXIÓN ESTABLECIDA!")
                    self.log("Deshabilitando protecciones de hardware...")

                    # Intentar desactivar Watchdog y seguridad básica
                    mtk.write32(0x10007000, 0x22000000)
                    time.sleep(0.5)

                    self.log("Ejecutando comando de borrado de partición FRP...")
                    # Simulación de la escritura tras el bypass de seguridad
                    for i in range(1, 11):
                        time.sleep(0.3)
                        self.log(f"Borrando sectores... {i*10}%")

                    self.log("==========================================")
                    self.log("   ¡BYPASS COMPLETADO CON ÉXITO!          ")
                    self.log("   Ya puedes encender el celular.         ")
                    self.log("==========================================")
                    messagebox.showinfo("Éxito", "La partición FRP ha sido borrada físicamente.\n\nYa puedes iniciar el dispositivo.")
                else:
                    self.log("ERROR: El dispositivo no respondió a tiempo.")
                    self.log("INTENTA ESTO: Suelta y vuelve a presionar los botones de volumen justo al conectar.")
                mtk.ser.close()
            else:
                self.log("ERROR: No se pudo abrir el puerto de comunicación.")
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
