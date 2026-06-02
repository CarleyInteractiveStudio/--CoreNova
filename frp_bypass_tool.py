import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import time
import os
from lib.qualcomm import QualcommEDL, QUnlocker
from lib.qchips import QCHIPS
from lib.bruteforce import BruteForceModule

class QcomUnlockTool:
    def __init__(self, root):
        self.root = root
        self.root.title("QUALCOMM PRO UNLOCKER v1.0 (EDL MODE)")
        self.root.geometry("1100x950")
        self.root.configure(bg="#050505")

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#050505", borderwidth=0)
        style.configure("TNotebook.Tab", background="#222", foreground="#ccc", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#333")], foreground=[("selected", "#fff")])

        self.header = tk.Label(root, text="QUALCOMM PRO UNLOCKER: EDL EDITION", font=("Courier New", 24, "bold"), fg="#00ffff", bg="#050505")
        self.header.pack(pady=20)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Control Principal
        self.main_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.main_tab, text="CONTROL PRINCIPAL")
        self.setup_main_tab()

        # Tab 2: Guía de Conexión
        self.guide_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.guide_tab, text="GUÍA DE CONEXIÓN")
        self.setup_guide_tab()

        # Tab 3: Fuerza Bruta
        self.bf_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.bf_tab, text="FUERZA BRUTA (OFFLINE)")
        self.setup_bf_tab()

        # Tab 4: Logs
        self.log_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.log_tab, text="LOGS TÉCNICOS")
        self.setup_log_tab()

        self.bruteforcer = BruteForceModule(log_callback=self.log)
        self.running = False
        self.active_ser = False
        self.qcom_proto = None

    def log(self, msg, level="INFO"):
        ts = time.strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{ts}] [{level}] {msg}\n")
        self.log_area.see(tk.END)

    def setup_main_tab(self):
        frame = tk.Frame(self.main_tab, bg="#0a0a0a", padx=20, pady=20)
        frame.pack(fill=tk.BOTH)

        tk.Label(frame, text="SELECCIONAR MODELO/CHIPSET:", bg="#0a0a0a", fg="#00ff00").pack(pady=5)
        self.chip_var = tk.StringVar()
        chip_names = [f"{v['name']} ({k})" for k, v in QCHIPS.items()]
        self.chip_combo = ttk.Combobox(frame, textvariable=self.chip_var, values=chip_names, state="readonly")
        self.chip_combo.pack(fill=tk.X, pady=5)
        self.chip_combo.current(0)

        self.btn_action = tk.Button(frame, text="CONECTAR DISPOSITIVO (MODO 9008)", command=self.run_connect,
                                   bg="#004444", fg="#00ffff", font=("Consolas", 12, "bold"), height=2)
        self.btn_action.pack(fill=tk.X, pady=20)

        self.btn_remove_lock = tk.Button(frame, text="QUITAR BLOQUEO PANTALLA (SIN BORRAR DATOS)",
                                        command=self.run_qcom_unlock,
                                        bg="#000044", fg="#8888ff", font=("Consolas", 12, "bold"), height=2)
        self.btn_remove_lock.pack(fill=tk.X, pady=10)

        self.btn_format = tk.Button(frame, text="BORRAR CUENTA GOOGLE (FRP)", command=self.run_qcom_frp,
                                   bg="#440000", fg="#ff0000", font=("Consolas", 12, "bold"), height=2)
        self.btn_format.pack(fill=tk.X, pady=10)

        tk.Label(frame, text="ESTADO DEL HARDWARE:", bg="#0a0a0a", fg="#aaa").pack(pady=5)
        self.hw_info = tk.Label(frame, text="ESPERANDO DISPOSITIVO...", font=("Consolas", 14), bg="#111", fg="#fff", padx=10, pady=5)
        self.hw_info.pack(fill=tk.X)

    def setup_guide_tab(self):
        guide = scrolledtext.ScrolledText(self.guide_tab, bg="#000", fg="#ccc", font=("Consolas", 11), padx=20, pady=20)
        guide.pack(fill=tk.BOTH, expand=True)

        content = """
PASOS PARA CONECTAR TU BLACKBERRY KEYONE EN MODO EDL (9008):

1. APAGAR EL TELÉFONO COMPLETAMENTE.
2. PREPARAR EL CABLE USB (QUE ESTÉ CONECTADO A LA PC).
3. PRESIONAR Y MANTENER LOS BOTONES:
   [ VOLUMEN ARRIBA ] + [ VOLUMEN ABAJO ]
4. MIENTRAS MANTIENES LOS BOTONES, CONECTA EL CABLE USB.
5. LA PANTALLA SE QUEDARÁ NEGRA (ES NORMAL).
6. EN EL ADMINISTRADOR DE DISPOSITIVOS DE WINDOWS DEBERÍAS VER:
   "Qualcomm HS-USB QDLoader 9008"

SI NO APARECE:
- INTENTA CON LA COMBINACIÓN: [ VOLUMEN ARRIBA ] + [ ENCENDIDO ].
- ASEGÚRATE DE TENER LOS DRIVERS DE QUALCOMM INSTALADOS.
- ALGUNOS CABLES REQUIEREN UN "EDL CABLE" ESPECIAL SI EL TELÉFONO ESTÁ MUY BLOQUEADO.

UNA VEZ CONECTADO, VE A LA PESTAÑA 'CONTROL PRINCIPAL' Y DALE A 'CONECTAR'.
        """
        guide.insert(tk.END, content)
        guide.config(state=tk.DISABLED)

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
        try:
            l = int(self.len_entry.get().strip())
        except:
            l = 4

        def task():
            res = self.bruteforcer.crack_sha1_salt(h, s, max_len=l)
            messagebox.showinfo("Resultado Fuerza Bruta", res)

        threading.Thread(target=task, daemon=True).start()

    def setup_log_tab(self):
        self.log_area = scrolledtext.ScrolledText(self.log_tab, bg="#000", fg="#00ff00", font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def run_connect(self):
        if not self.running:
            threading.Thread(target=self.connect_logic, daemon=True).start()

    def connect_logic(self):
        self.running = True
        self.log("Buscando dispositivo Qualcomm en puerto COM...")

        port = self.find_device_port("05C6") # Qualcomm VID
        if port:
            self.qcom_proto = QualcommEDL()
            self.qcom_proto.connect(port)
            if self.qcom_proto.sahara_handshake():
                self.log(f"¡CONECTADO! Dispositivo detectado en {port}.")
                self.hw_info.config(text=f"QUALCOMM EDL ACTIVO ({port})", fg="#00ffff")
                self.active_ser = True
            else:
                self.log("Fallo en handshake Sahara. Verifica drivers.", "ERROR")
        else:
            self.log("No se detectó el puerto 9008. Revisa la Guía de Conexión.", "WARN")

        self.running = False

    def find_device_port(self, vid_pattern):
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            if vid_pattern.upper() in p.hwid.upper():
                return p.device
        return None

    def run_qcom_unlock(self):
        if not self.qcom_proto or not self.active_ser:
            self.log("Conecta el teléfono primero.", "WARN")
            return

        unlocker = QUnlocker(self.qcom_proto)
        res = unlocker.remove_lock_screen()
        self.log(res)
        messagebox.showinfo("Qualcomm Unlock", res)

    def run_qcom_frp(self):
        if not self.qcom_proto or not self.active_ser:
            self.log("Conecta el teléfono primero.", "WARN")
            return

        unlocker = QUnlocker(self.qcom_proto)
        res = unlocker.bypass_frp()
        self.log(res)
        messagebox.showinfo("Qualcomm FRP", res)

if __name__ == "__main__":
    root = tk.Tk()
    app = QcomUnlockTool(root)
    root.mainloop()
