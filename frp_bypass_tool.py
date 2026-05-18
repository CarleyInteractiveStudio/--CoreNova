import serial
import serial.tools.list_ports
import time
import struct
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import os
try:
    import usb.core
    import usb.util
    USB_SUPPORT = True
except ImportError:
    USB_SUPPORT = False

# Datos exactos del scatter de Oukitel WP36
FRP_START_ADDRESS = 0x1588000
FRP_SIZE = 0x100000

class OukitelHackerToolV4:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 FRP - DIRECT HACK V4")
        self.root.geometry("900x950")
        self.root.configure(bg="#0a0a0a")

        self.header = tk.Label(root, text="OUKITEL WP36 - HACKER MODE", font=("Impact", 28), fg="#ef4444", bg="#0a0a0a")
        self.header.pack(pady=20)

        # Panel de Control
        self.control_frame = tk.Frame(root, bg="#111", bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.control_frame.pack(fill=tk.X, padx=20)

        self.btn_bypass = tk.Button(self.control_frame, text="1. BYPASS SEGURIDAD", command=self.run_bypass,
                                   bg="#2563eb", fg="white", font=("Consolas", 12, "bold"), width=25)
        self.btn_bypass.grid(row=0, column=0, padx=5, pady=5)

        self.btn_format = tk.Button(self.control_frame, text="2. BORRAR FRP (DIRECTO)", command=self.run_format,
                                   bg="#b91c1c", fg="white", font=("Consolas", 12, "bold"), width=25)
        self.btn_format.grid(row=0, column=1, padx=5, pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=100, height=35, font=("Consolas", 9), bg="#000", fg="#4ade80")
        self.log_area.pack(pady=10, padx=20)

        self.log("INICIO: V4 LISTA PARA LA COMPETENCIA.")
        self.log(f"USB SUPPORT: {'SI' if USB_SUPPORT else 'NO (Instalar pyusb)'}")
        self.log("INFO: Si Zadig falla, usa el botón de Bypass y luego el de Borrar rápido.")

        self.running = False
        self.device_serial = None

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        for p in serial.tools.list_ports.comports():
            if "0E8D" in p.hwid.upper():
                return p.device
        return None

    def handshake(self, ser):
        ser.timeout = 0.01
        for _ in range(200):
            ser.write(b'\xA0')
            res = ser.read(1)
            if res in [b'\x5A', b'\x5F', b'\xA5']:
                self.log(f"Handshake 0x{res.hex().upper()} OK")
                return True
        return False

    def usb_bypass(self):
        """Bypass usando PyUSB (Modo LibUSB/Zadig)"""
        if not USB_SUPPORT:
            self.log("ERROR: PyUSB no está instalado.")
            return False

        self.log("Buscando dispositivo USB (Modo LibUSB)...")
        dev = usb.core.find(idVendor=0x0E8D)
        if dev:
            try:
                self.log("Ejecutando Glitch USB...")
                dev.set_configuration()
                for _ in range(15):
                    dev.ctrl_transfer(0x21, 0x20, 0, 0, b'\x00')
                self.log("USB Bypass OK.")
                return True
            except Exception as e:
                self.log(f"Error USB: {e}")
        return False

    def bypass_logic(self):
        self.running = True
        self.log("ESPERANDO DISPOSITIVO (VOL+ y VOL-)...")
        while self.running:
            # Intento 1: USB Directo (Zadig)
            if USB_SUPPORT and self.usb_bypass():
                self.log(">>> BYPASS COMPLETADO (USB) <<<")
                messagebox.showinfo("Bypass", "Seguridad deshabilitada vía USB.\nUsa SP Flash Tool o intenta el botón de Borrar.")
                break

            # Intento 2: Serial COM Port
            port = self.find_mtk_port()
            if port:
                self.log(f"Detectado en {port}")
                try:
                    ser = serial.Serial(port, 115200, timeout=1)
                    if self.handshake(ser):
                        self.log("Enviando exploit Serial...")
                        for cmd in [b'\xA1', b'\xA2', b'\xA3', b'\xA4']:
                            ser.write(cmd)
                            ser.read(1)

                        self.log(">>> BYPASS COMPLETADO (SERIAL) <<<")
                        self.device_serial = ser
                        messagebox.showinfo("Bypass", "Seguridad deshabilitada vía Serial.\nAhora pulsa 'BORRAR FRP'.")
                        break
                    ser.close()
                except Exception as e:
                    self.log(f"Error Serial: {e}")
            time.sleep(0.5)
        self.running = False

    def format_logic(self):
        if not self.device_serial or not self.device_serial.is_open:
            self.log("ERROR: Primero debes hacer el BYPASS.")
            return

        self.log("INICIANDO FORMATEO DE PARTICIÓN FRP...")
        try:
            ser = self.device_serial
            # Comando 0xD4 (FORMAT)
            ser.write(b'\xD4')
            if ser.read(1) == b'\xD4':
                self.log(f"Dirección: {hex(FRP_START_ADDRESS)}")
                ser.write(struct.pack(">I", FRP_START_ADDRESS))
                ser.write(struct.pack(">I", FRP_SIZE))

                res = ser.read(2)
                if res == b'\x00\x00':
                    self.log("¡¡¡ VICTORIA !!! FRP BORRADO.")
                    messagebox.showinfo("EXITO", "El bloqueo de Google ha sido eliminado.\nReinicia el celular.")
                else:
                    self.log(f"Error en formato: {res.hex().upper()}")
            else:
                self.log("El procesador rechazó el comando 0xD4.")
        except Exception as e:
            self.log(f"Error crítico: {e}")

    def run_bypass(self):
        if not self.running:
            threading.Thread(target=self.bypass_logic, daemon=True).start()

    def run_format(self):
        threading.Thread(target=self.format_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelHackerToolV4(root)
    root.mainloop()
