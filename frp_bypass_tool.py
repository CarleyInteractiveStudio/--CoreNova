import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import time
import os
from lib.brom import MTKProtocol
from lib.payloads import Kamakiri
from lib.chips import CHIPS
from lib.qualcomm import QualcommEDL, QUnlocker
from lib.qchips import QCHIPS
from lib.bruteforce import BruteForceModule

class AdvancedMtkTool:
    def __init__(self, root):
        self.root = root
        self.root.title("UNIVERSAL MOBILE UNLOCKER V6 (PRO EDITION)")
        self.root.geometry("1100x950")
        self.root.configure(bg="#050505")

        self.arch_mode = tk.StringVar(value="MTK")

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#050505", borderwidth=0)
        style.configure("TNotebook.Tab", background="#222", foreground="#ccc", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#333")], foreground=[("selected", "#fff")])

        self.header = tk.Label(root, text="UNIVERSAL MOBILE UNLOCKER V6", font=("Courier New", 24, "bold"), fg="#00ffff", bg="#050505")
        self.header.pack(pady=20)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Main Control
        self.main_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.main_tab, text="CONTROL PRINCIPAL")
        self.setup_main_tab()

        # Tab 2: Brute Force
        self.bf_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.bf_tab, text="FUERZA BRUTA (OFFLINE)")
        self.setup_bf_tab()

        # Tab 3: Memory Operations
        self.mem_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.mem_tab, text="MEMORIA (DMA)")
        self.setup_mem_tab()

        # Tab 4: Logs
        self.log_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.log_tab, text="LOGS TÉCNICOS")
        self.setup_log_tab()

        self.protocol = MTKProtocol()
        self.kamakiri = Kamakiri()
        self.bruteforcer = BruteForceModule(log_callback=self.log)
        self.running = False
        self.active_ser = None

    def log(self, msg, level="INFO"):
        ts = time.strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{ts}] [{level}] {msg}\n")
        self.log_area.see(tk.END)

    def setup_main_tab(self):
        frame = tk.Frame(self.main_tab, bg="#0a0a0a", padx=20, pady=20)
        frame.pack(fill=tk.BOTH)

        # Selección de Arquitectura
        tk.Label(frame, text="ARQUITECTURA DEL DISPOSITIVO:", bg="#0a0a0a", fg="#00ffff").pack(pady=5)
        arch_frame = tk.Frame(frame, bg="#0a0a0a")
        arch_frame.pack(pady=5)
        tk.Radiobutton(arch_frame, text="MediaTek (MTK)", variable=self.arch_mode, value="MTK",
                       bg="#0a0a0a", fg="#fff", selectcolor="#222", command=self.update_chip_list).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(arch_frame, text="Qualcomm (EDL)", variable=self.arch_mode, value="QCOM",
                       bg="#0a0a0a", fg="#fff", selectcolor="#222", command=self.update_chip_list).pack(side=tk.LEFT, padx=10)

        # Selección de Chipset
        tk.Label(frame, text="SELECCIONAR MODELO/CHIPSET:", bg="#0a0a0a", fg="#00ff00").pack(pady=5)
        self.chip_var = tk.StringVar()
        self.chip_combo = ttk.Combobox(frame, textvariable=self.chip_var, state="readonly")
        self.chip_combo.pack(fill=tk.X, pady=5)

        self.btn_action = tk.Button(frame, text="INICIAR CONEXIÓN / BYPASS", command=self.run_bypass,
                                   bg="#004400", fg="#00ff00", font=("Consolas", 12, "bold"), height=2)
        self.btn_action.pack(fill=tk.X, pady=10)

        self.qcom_frame = tk.Frame(frame, bg="#0a0a0a")

        self.btn_remove_lock = tk.Button(self.qcom_frame, text="QUITAR BLOQUEO PANTALLA (SIN BORRAR DATOS)",
                                        command=self.run_qcom_unlock,
                                        bg="#000044", fg="#8888ff", font=("Consolas", 12, "bold"), height=2)

        self.btn_format = tk.Button(frame, text="BORRAR CUENTA GOOGLE (FRP)", command=self.run_format,
                                   bg="#440000", fg="#ff0000", font=("Consolas", 12, "bold"), height=2)
        self.btn_format.pack(fill=tk.X, pady=10)

        tk.Label(frame, text="ESTADO DEL HARDWARE:", bg="#0a0a0a", fg="#aaa").pack(pady=5)
        self.hw_info = tk.Label(frame, text="DESCONECTADO", font=("Consolas", 14), bg="#111", fg="#fff", padx=10, pady=5)
        self.hw_info.pack(fill=tk.X)

        self.update_chip_list()

    def setup_bf_tab(self):
        frame = tk.Frame(self.bf_tab, bg="#0a0a0a", padx=20, pady=20)
        frame.pack(fill=tk.BOTH)

        tk.Label(frame, text="CRACKEO DE HASH (Android locksettings.db)", bg="#0a0a0a", fg="#fbbf24", font=("Consolas", 14)).pack(pady=10)

        tk.Label(frame, text="HASH (HEX):", bg="#0a0a0a", fg="#fff").pack()
        self.hash_entry = tk.Entry(frame, bg="#222", fg="#fff", width=60)
        self.hash_entry.pack(pady=5)

        tk.Label(frame, text="SALT (HEX):", bg="#0a0a0a", fg="#fff").pack()
        self.salt_entry = tk.Entry(frame, bg="#222", fg="#fff", width=60)
        self.salt_entry.pack(pady=5)

        tk.Label(frame, text="MÁXIMA LONGITUD (PIN):", bg="#0a0a0a", fg="#fff").pack()
        self.len_entry = tk.Entry(frame, bg="#222", fg="#fff", width=10)
        self.len_entry.insert(0, "4")
        self.len_entry.pack(pady=5)

        self.btn_crack = tk.Button(frame, text="INICIAR ATAQUE DE FUERZA BRUTA", command=self.run_bruteforce,
                                  bg="#78350f", fg="#fff", font=("Consolas", 12, "bold"), height=2)
        self.btn_crack.pack(fill=tk.X, pady=20)

    def run_bruteforce(self):
        h = self.hash_entry.get().strip()
        s = self.salt_entry.get().strip()
        l = int(self.len_entry.get().strip())

        def task():
            res = self.bruteforcer.crack_sha1_salt(h, s, max_len=l)
            messagebox.showinfo("Resultado Fuerza Bruta", res)

        threading.Thread(target=task, daemon=True).start()

    def update_chip_list(self):
        if self.arch_mode.get() == "MTK":
            chip_names = [f"{v['name']} ({k})" for k, v in CHIPS.items()]
            if hasattr(self, 'qcom_frame'): self.qcom_frame.pack_forget()
        else:
            chip_names = [f"{v['name']} ({k})" for k, v in QCHIPS.items()]
            if hasattr(self, 'qcom_frame'):
                self.qcom_frame.pack(fill=tk.X, pady=5)
                self.btn_remove_lock.pack(fill=tk.X, pady=5)

        self.chip_combo['values'] = chip_names
        if chip_names:
            self.chip_combo.current(0)

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

    def setup_log_tab(self):
        self.log_area = scrolledtext.ScrolledText(self.log_tab, bg="#000", fg="#00ff00", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def run_bypass(self):
        if not self.running:
            threading.Thread(target=self.bypass_logic, daemon=True).start()

    def get_selected_chip(self):
        selected = self.chip_var.get()
        if not "(" in selected: return None
        hw_code = selected.split("(")[1].split(")")[0]
        if self.arch_mode.get() == "MTK":
            return CHIPS[hw_code]
        else:
            return QCHIPS[hw_code]

    def bypass_logic(self):
        self.running = True
        arch = self.arch_mode.get()
        self.log(f"Iniciando conexión para {arch}...")

        if arch == "MTK":
            ok, msg = self.kamakiri.exploit()
            if ok: self.log("Bypass USB exitoso.")

            port = self.find_device_port("0E8D")
            if port:
                self.protocol.connect(port)
                if self.protocol.handshake():
                    self.log("Conectado a MediaTek.")
                    self.hw_info.config(text="MTK CONNECTED", fg="#00ff00")
                    self.active_ser = True
            else:
                self.log("No se encontró dispositivo MTK.", "ERROR")

        elif arch == "QCOM":
            port = self.find_device_port("05C6")
            if port:
                self.qcom_proto = QualcommEDL()
                self.qcom_proto.connect(port)
                if self.qcom_proto.sahara_handshake():
                    self.log("Conectado vía Sahara (EDL).")
                    self.hw_info.config(text="QUALCOMM EDL READY", fg="#00ffff")
                    self.active_ser = True
                    self.log("Cargando programador Firehose...")
                else:
                    self.log("Error en Handshake Sahara.", "ERROR")
            else:
                self.log("No se encontró dispositivo Qualcomm en modo 9008.", "ERROR")

        self.running = False

    def find_device_port(self, vid_pattern):
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            if vid_pattern.upper() in p.hwid.upper():
                return p.device
        return None

    def run_qcom_unlock(self):
        if not hasattr(self, 'qcom_proto') or not self.active_ser:
            self.log("Conecta el dispositivo en modo EDL primero.", "WARN")
            return

        unlocker = QUnlocker(self.qcom_proto)
        res = unlocker.remove_lock_screen()
        self.log(res)
        messagebox.showinfo("Qualcomm Unlock", res)

    def run_format(self):
        if self.active_ser:
            chip = self.get_selected_chip()
            if not chip: return

            if self.arch_mode.get() == "MTK":
                addr = chip.get('frp_address', 0)
                size = chip.get('frp_size', 0)
                if addr == 0:
                    self.log("Este modelo no tiene dirección FRP definida.", "ERROR")
                    return
                self.log(f"Formateando {chip['name']} en {hex(addr)}...")
                if self.protocol.format_partition(addr, size):
                    self.log("PARTICIÓN FORMATEADA CON ÉXITO.")
                    messagebox.showinfo("Éxito", f"FRP de {chip['name']} borrado.")
                else:
                    self.log("Error al formatear.", "ERROR")
            else:
                unlocker = QUnlocker(self.qcom_proto)
                res = unlocker.bypass_frp()
                self.log(res)
                messagebox.showinfo("Qualcomm FRP", res)
        else:
            self.log("Realiza el BYPASS primero.", "WARN")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedMtkTool(root)
    root.mainloop()
