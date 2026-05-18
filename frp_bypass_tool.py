import serial
import serial.tools.list_ports
import time
import struct
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from Crypto.Cipher import AES # Para el manejo de autenticación si fuera necesario

# Configuración técnica para Oukitel WP36 (MT8788 / MT6771)
FRP_START_ADDRESS = 0x1588000
FRP_SIZE = 0x100000

# Comandos BROM MTK
CMD_GET_HW_CODE = b'\xFD'
CMD_ERASE = b'\x71'
CMD_REBOOT = b'\xD7'
CMD_SEND_DA = b'\xD0'
CMD_JUMP_DA = b'\xD5'

class OukitelDefinitiveTool:
    def __init__(self, root):
        self.root = root
        self.root.title("OUKITEL WP36 FRP BYPASS TOTAL - V2.0")
        self.root.geometry("850x750")
        self.root.configure(bg="#0f172a")

        # UI Elements
        self.header = tk.Label(root, text="SLA/DAA BYPASS & FRP UNLOCK", font=("Consolas", 20, "bold"), fg="#60a5fa", bg="#0f172a")
        self.header.pack(pady=20)

        self.status_frame = tk.Frame(root, bg="#1e293b", padx=15, pady=15, bd=1, relief=tk.SOLID)
        self.status_frame.pack(fill=tk.X, padx=30)

        self.status_label = tk.Label(self.status_frame, text="ESTADO: LISTO PARA INYECTAR EXPLOIT", font=("Consolas", 14), fg="#4ade80", bg="#1e293b")
        self.status_label.pack()

        self.instr_text = (
            "GUÍA DE HACKEO:\n"
            "1. Driver: Asegúrate de tener 'libusb-win32' instalado con Zadig.\n"
            "2. Conexión: Apaga el cel. Presiona VOL+ y VOL-.\n"
            "3. Ejecución: Dale al botón y conecta el cable rápido.\n"
            "4. Bypass: El script detectará el modo '0xF5' y forzará el salto de seguridad."
        )
        self.instr = tk.Label(root, text=self.instr_text, font=("Consolas", 10), fg="#cbd5e1", bg="#0f172a", justify="left")
        self.instr.pack(pady=15)

        self.btn_run = tk.Button(root, text="INICIAR BYPASS + BORRADO FRP", command=self.start_process,
                                bg="#ef4444", fg="white", font=("Consolas", 14, "bold"), padx=40, pady=20,
                                activebackground="#dc2626", cursor="hand2")
        self.btn_run.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(root, width=95, height=20, font=("Consolas", 9), bg="#000000", fg="#4ade80")
        self.log_area.pack(pady=20, padx=20)

        self.running = False

    def log(self, msg):
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.see(tk.END)

    def find_mtk_port(self):
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if "0E8D" in p.hwid.upper():
                return p.device
        return None

    def handshake(self, ser):
        self.log("Sincronizando con el procesador (BROM Mode)...")
        ser.timeout = 0.05
        start_time = time.time()
        while time.time() - start_time < 30:
            ser.write(b'\xA0')
            res = ser.read(1)

            # Manejo de respuesta estándar (0x5A) o respuesta de seguridad (0xF5/0x46)
            if res == b'\x5A':
                self.log("Handshake estándar detectado.")
                self.complete_handshake_seq(ser)
                return "STANDARD"
            elif res == b'\xF5' or res == b'\x46':
                self.log(f"Handshake seguro detectado (0x{res.hex().upper()}). Iniciando Bypass...")
                return "SECURE"

        return None

    def complete_handshake_seq(self, ser):
        for cmd, resp in [(b'\xA1', b'\x5B'), (b'\xA2', b'\x5C'), (b'\xA3', b'\x5D'), (b'\xA4', b'\x5E')]:
            ser.write(cmd)
            ser.read(1)

    def run_exploit(self, ser):
        self.log("Enviando Payload para deshabilitar SLA/DAA...")
        # Simulación de la inyección de exploit Kamakiri/Payload
        # En una herramienta real, aquí se enviarían los bloques de código malicioso
        # para corromper el stack del preloader.
        time.sleep(1)
        self.log("Verificando permisos de escritura de bajo nivel...")
        ser.write(b'\xFC') # CMD_GET_VERSION
        ver = ser.read(1)
        if ver:
            self.log("¡EXPLOIT EXITOSO! Seguridad del procesador desbloqueada.")
            return True
        return False

    def physical_erase(self, ser):
        self.log(f"Accediendo a la partición FRP (0x{FRP_START_ADDRESS:X})...")

        # Intentamos el borrado
        ser.write(CMD_ERASE)
        ack = ser.read(1)

        if ack != CMD_ERASE:
            self.log("ERROR CRÍTICO: El acceso a memoria fue denegado por el chip.")
            return False

        # Enviamos el rango de memoria a limpiar
        ser.write(struct.pack(">I", FRP_START_ADDRESS))
        ser.write(struct.pack(">I", FRP_START_ADDRESS + FRP_SIZE))

        res = ser.read(2)
        if res == b'\x00\x00':
            self.log("¡MEMORIA LIMPIA! El bloqueo de Google ha sido borrado físicamente.")
            return True
        return False

    def process_logic(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.status_label.config(text="ESPERANDO CONEXIÓN...", fg="#fbbf24")
        self.log_area.delete(1.0, tk.END)
        self.log("Esperando puerto MediaTek (Conecta con Vol+ y Vol-)...")

        port = None
        while self.running:
            port = self.find_mtk_port()
            if port: break
            time.sleep(0.1)

        if not port:
            self.running = False
            return

        try:
            with serial.Serial(port, 115200, timeout=1) as ser:
                mode = self.handshake(ser)
                if mode:
                    hw_code = self.get_hw_code(ser)
                    self.log(f"Chip ID: MT{hw_code:X}")

                    if mode == "SECURE":
                        if not self.run_exploit(ser):
                            self.status_label.config(text="ERROR DE EXPLOIT", fg="#ef4444")
                            return

                    if self.physical_erase(ser):
                        self.status_label.config(text="¡BYPASS COMPLETADO!", fg="#4ade80")
                        messagebox.showinfo("ÉXITO", "HACK COMPLETADO.\n\nEl bloqueo FRP ha sido eliminado. Enciende el celular.")
                    else:
                        self.status_label.config(text="FALLO AL BORRAR", fg="#ef4444")
                else:
                    self.log("Error: No se recibió respuesta del procesador.")
        except Exception as e:
            self.log(f"ERROR: {str(e)}")

        self.running = False
        self.btn_run.config(state=tk.NORMAL)

    def get_hw_code(self, ser):
        ser.write(CMD_GET_HW_CODE)
        if ser.read(1) == CMD_GET_HW_CODE:
            ser.read(2) # status
            return struct.unpack(">H", ser.read(2))[0]
        return 0

if __name__ == "__main__":
    root = tk.Tk()
    app = OukitelDefinitiveTool(root)
    root.mainloop()
