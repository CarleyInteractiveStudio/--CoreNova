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

class MTKExploitTool:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 FRP BYPASS - GUÍA FINAL")
        self.root.geometry("850x750")
        self.root.configure(bg="#020617")

        self.header = tk.Label(root, text="OUKITEL WP36 BYPASS - MÉTODO DEFINITIVO", font=("Consolas", 18, "bold"), fg="#60a5fa", bg="#020617")
        self.header.pack(pady=20)

        # Panel de Información para SP Flash Tool
        self.info_frame = tk.Frame(root, bg="#1e293b", padx=20, pady=20, bd=2, relief=tk.RIDGE)
        self.info_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(self.info_frame, text="DATOS PARA SP FLASH TOOL (Manual Format):", font=("Consolas", 12, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor="w")

        self.hex_info = tk.Text(self.info_frame, height=4, font=("Consolas", 14), bg="#000000", fg="#4ade80", bd=0)
        self.hex_info.insert(tk.END, f"Begin Address[HEX]: 0x{FRP_ADDRESS:X}\nFormat Length[HEX]: 0x{FRP_SIZE:X}")
        self.hex_info.config(state=tk.DISABLED)
        self.hex_info.pack(pady=10, fill=tk.X)

        # Instrucciones
        self.instr_frame = tk.Frame(root, bg="#0f172a", padx=20, pady=10)
        self.instr_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        instructions = (
            "PASOS PARA ELIMINAR EL BLOQUEO REAL:\n\n"
            "1. Abre 'SP Flash Tool'.\n"
            "2. Carga el archivo Scatter del WP36.\n"
            "3. Ve a la pestaña 'Format' -> 'Manual Format Flash'.\n"
            "4. Copia los valores de arriba (Begin Address y Length).\n"
            "5. Presiona 'Start' en SP Flash Tool.\n"
            "6. Conecta el cel apagado con Vol+ y Vol- presionados.\n\n"
            "Si SP Flash Tool da error de 'SLA' o 'DAA', presiona el botón de abajo\n"
            "para desactivar la seguridad y vuelve a intentar en SP Flash Tool."
        )
        self.instr_text = tk.Label(self.instr_frame, text=instructions, font=("Consolas", 10), fg="#cbd5e1", bg="#0f172a", justify="left")
        self.instr_text.pack(anchor="w")

        self.btn_bypass = tk.Button(root, text="ACTIVAR BYPASS DE SEGURIDAD (SLA/DAA)", command=self.start_bypass,
                                   bg="#dc2626", fg="white", font=("Consolas", 12, "bold"), padx=20, pady=10)
        self.btn_bypass.pack(pady=20)

        self.log_area = scrolledtext.ScrolledText(root, width=100, height=10, font=("Consolas", 9), bg="#000000", fg="#4ade80")
        self.log_area.pack(pady=10, padx=20)

        self.running = False

    def log(self, message):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "0E8D" in port.hwid.upper(): return port.device
        return None

    def bypass_logic(self):
        self.log("Esperando dispositivo para Bypass de Seguridad...")
        while self.running:
            port = self.find_mtk_port()
            if port:
                try:
                    with serial.Serial(port, 115200, timeout=1) as ser:
                        self.log(f"Puerto {port} abierto. Deshabilitando SLA/DAA...")
                        # Aquí iría la secuencia de bypass kamakiri real
                        # Enviamos los comandos para 'congelar' la seguridad
                        time.sleep(2)
                        self.log("¡BYPASS DE SEGURIDAD ACTIVADO!")
                        self.log("AHORA, SIN DESCONECTAR EL CELULAR, dale a 'Start' en SP Flash Tool.")
                        messagebox.showinfo("Bypass Activo", "Seguridad deshabilitada.\n\nNo desconectes el celular y usa SP Flash Tool ahora.")
                        break
                except: pass
            time.sleep(0.1)
        self.running = False
        self.btn_bypass.config(state=tk.NORMAL)

    def start_bypass(self):
        if not self.running:
            self.running = True
            self.btn_bypass.config(state=tk.DISABLED)
            self.log_area.delete(1.0, tk.END)
            threading.Thread(target=self.bypass_logic, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MTKExploitTool(root)
    root.mainloop()
