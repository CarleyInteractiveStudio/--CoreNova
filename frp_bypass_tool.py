import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import time
import os
from lib.brom import MTKProtocol
from lib.payloads import Kamakiri
from lib.chips import CHIPS

class AdvancedMtkTool:
    def __init__(self, root):
        self.root = root
        self.root.title("ADVANCED MEDIA-HACK V5 (RESEARCH EDITION)")
        self.root.geometry("1000x900")
        self.root.configure(bg="#050505")

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#050505", borderwidth=0)
        style.configure("TNotebook.Tab", background="#222", foreground="#ccc", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#333")], foreground=[("selected", "#fff")])

        self.header = tk.Label(root, text="MEDIA-HACK V5: RESEARCH MODE", font=("Courier New", 24, "bold"), fg="#00ff00", bg="#050505")
        self.header.pack(pady=20)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Main Control
        self.main_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.main_tab, text="CONTROL PRINCIPAL")
        self.setup_main_tab()

        # Tab 2: Memory Operations
        self.mem_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.mem_tab, text="MEMORIA (DMA)")
        self.setup_mem_tab()

        # Tab 3: Payloads
        self.payload_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.payload_tab, text="PAYLOADS (AVANZADO)")
        self.setup_payload_tab()

        # Tab 4: Logs
        self.log_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.log_tab, text="LOGS TÉCNICOS")
        self.setup_log_tab()

        self.protocol = MTKProtocol()
        self.kamakiri = Kamakiri()
        self.running = False
        self.active_ser = None

    def log(self, msg, level="INFO"):
        ts = time.strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{ts}] [{level}] {msg}\n")
        self.log_area.see(tk.END)

    def setup_main_tab(self):
        frame = tk.Frame(self.main_tab, bg="#0a0a0a", padx=20, pady=20)
        frame.pack(fill=tk.BOTH)

        # Selección de Chipset
        tk.Label(frame, text="SELECCIONAR CHIPSET:", bg="#0a0a0a", fg="#00ff00").pack(pady=5)
        self.chip_var = tk.StringVar()
        chip_names = [f"{v['name']} ({k})" for k, v in CHIPS.items()]
        self.chip_combo = ttk.Combobox(frame, textvariable=self.chip_var, values=chip_names, state="readonly")
        self.chip_combo.pack(fill=tk.X, pady=5)
        self.chip_combo.current(0)

        self.btn_bypass = tk.Button(frame, text="EJECUTAR BYPASS (SLA/DAA)", command=self.run_bypass,
                                   bg="#004400", fg="#00ff00", font=("Consolas", 12, "bold"), height=2)
        self.btn_bypass.pack(fill=tk.X, pady=10)

        self.btn_format = tk.Button(frame, text="BORRAR PARTICIÓN FRP", command=self.run_format,
                                   bg="#440000", fg="#ff0000", font=("Consolas", 12, "bold"), height=2)
        self.btn_format.pack(fill=tk.X, pady=10)

        tk.Label(frame, text="ESTADO DEL HARDWARE:", bg="#0a0a0a", fg="#aaa").pack(pady=5)
        self.hw_info = tk.Label(frame, text="DESCONECTADO", font=("Consolas", 14), bg="#111", fg="#fff", padx=10, pady=5)
        self.hw_info.pack(fill=tk.X)

    def setup_mem_tab(self):
        frame = tk.Frame(self.mem_tab, bg="#0a0a0a", padx=20, pady=20)
        frame.pack(fill=tk.BOTH)

        tk.Label(frame, text="LEER REGIÓN DE MEMORIA", bg="#0a0a0a", fg="#00ff00").pack()

        input_frame = tk.Frame(frame, bg="#0a0a0a")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="ADDR:", bg="#0a0a0a", fg="#fff").grid(row=0, column=0)
        self.addr_entry = tk.Entry(input_frame, bg="#222", fg="#fff", width=15)
        self.addr_entry.insert(0, "0x1588000")
        self.addr_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="SIZE:", bg="#0a0a0a", fg="#fff").grid(row=0, column=2)
        self.size_entry = tk.Entry(input_frame, bg="#222", fg="#fff", width=15)
        self.size_entry.insert(0, "0x100")
        self.size_entry.grid(row=0, column=3, padx=5)

        self.btn_read = tk.Button(frame, text="LEER MEMORIA (HEX DUMP)", command=self.run_read,
                                 bg="#000044", fg="#5555ff", font=("Consolas", 10, "bold"))
        self.btn_read.pack(pady=10)

        self.hex_display = scrolledtext.ScrolledText(frame, bg="#000", fg="#4ade80", font=("Consolas", 9), height=25)
        self.hex_display.pack(fill=tk.BOTH, expand=True)

    def run_read(self):
        if not self.active_ser:
            self.log("Bypass primero.", "WARN")
            return

        try:
            addr = int(self.addr_entry.get(), 16)
            size = int(self.size_entry.get(), 16)
            self.log(f"Leyendo {size} bytes desde {hex(addr)}...")

            data = self.protocol.read_memory(addr, size)
            if data:
                self.hex_display.delete(1.0, tk.END)
                dump = ""
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    hex_part = " ".join(f"{b:02X}" for b in chunk)
                    ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                    dump += f"{hex(addr+i):<10} | {hex_part:<48} | {ascii_part}\n"
                self.hex_display.insert(tk.END, dump)
            else:
                self.log("Error al leer.", "ERROR")
        except Exception as e:
            self.log(f"Error: {e}", "ERROR")

    def setup_payload_tab(self):
        frame = tk.Frame(self.payload_tab, bg="#0a0a0a", padx=20, pady=20)
        frame.pack(fill=tk.BOTH)

        tk.Label(frame, text="CARGAR PAYLOAD DESDE ARCHIVO:", bg="#0a0a0a", fg="#fbbf24").pack()

        self.payload_list = tk.Listbox(frame, bg="#111", fg="#fff", font=("Consolas", 10))
        self.payload_list.pack(fill=tk.X, pady=10)
        self.refresh_payloads()

        self.btn_send_payload = tk.Button(frame, text="APLICAR PAYLOAD SELECCIONADO", command=self.run_payload,
                                         bg="#78350f", fg="#fff", font=("Consolas", 11, "bold"))
        self.btn_send_payload.pack(fill=tk.X)

    def refresh_payloads(self):
        if os.path.exists("payloads"):
            for f in os.listdir("payloads"):
                if f.endswith(".txt"):
                    self.payload_list.insert(tk.END, f)

    def run_payload(self):
        if not self.active_ser:
            self.log("Bypass primero.", "WARN")
            return

        selection = self.payload_list.curselection()
        if not selection:
            return

        filename = self.payload_list.get(selection[0])
        self.log(f"Cargando payload: {filename}")

        payload_data = {}
        try:
            with open(f"payloads/{filename}", "r") as f:
                for line in f:
                    if ":" in line and not line.startswith("#"):
                        addr, val = line.split(":")
                        payload_data[int(addr.strip(), 16)] = int(val.strip(), 16)

            if self.protocol.send_payload(payload_data):
                self.log("Payload aplicado correctamente.")
                messagebox.showinfo("Payload", "Inyección exitosa.")
            else:
                self.log("Error al aplicar payload.", "ERROR")
        except Exception as e:
            self.log(f"Error: {e}", "ERROR")

    def setup_log_tab(self):
        self.log_area = scrolledtext.ScrolledText(self.log_tab, bg="#000", fg="#00ff00", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def run_bypass(self):
        if not self.running:
            threading.Thread(target=self.bypass_logic, daemon=True).start()

    def get_selected_chip(self):
        selected = self.chip_var.get()
        hw_code = selected.split("(")[1].split(")")[0]
        return CHIPS[hw_code]

    def bypass_logic(self):
        self.running = True
        self.log("Buscando dispositivo...")

        # Primero intentamos USB Exploit
        ok, msg = self.kamakiri.exploit()
        if ok:
            self.log("Bypass USB (Kamakiri) exitoso.")
            # Después del exploit USB, el dispositivo suele reaparecer como COM port
            # o permite comunicación directa si el driver es el correcto.
            self.log("Esperando a que el puerto COM se estabilice...")
            time.sleep(2)
        else:
            self.log(f"USB falló o no disponible: {msg}")

        # Siempre intentamos conectar vía Serial para las operaciones de memoria
        port = self.find_mtk_port()
        if port:
            self.log(f"Conectando a {port}...")
            ser = self.protocol.connect(port)
            if self.protocol.handshake():
                hw_code = self.protocol.get_hw_code()
                self.log(f"Handshake exitoso. HW_CODE: {hex(hw_code) if hw_code else 'Desconocido'}")
                self.hw_info.config(text=f"BYPASS READY (HW: {hex(hw_code) if hw_code else '???'})", fg="#00ff00")
                self.active_ser = ser
            else:
                self.log("Handshake falló. Es posible que necesites re-conectar el cable.", "ERROR")
        else:
            self.log("No se detectó puerto COM. ¿Instalaste los drivers VCOM?", "ERROR")

        self.running = False

    def run_format(self):
        if self.active_ser:
            chip = self.get_selected_chip()
            addr = chip['frp_address']
            size = chip['frp_size']

            self.log(f"Formateando {chip['name']} en {hex(addr)}...")
            if self.protocol.format_partition(addr, size):
                self.log("PARTICIÓN FORMATEADA CON ÉXITO.")
                messagebox.showinfo("Éxito", f"FRP de {chip['name']} borrado.")
            else:
                self.log("Error al formatear. ¿Bypass activo?", "ERROR")
        else:
            self.log("Realiza el BYPASS primero.", "WARN")

    def find_mtk_port(self):
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            if "0E8D" in p.hwid.upper():
                return p.device
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedMtkTool(root)
    root.mainloop()
