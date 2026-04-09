import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from src.core.cracker import MD5Cracker, BruteForceCracker
from src.core.md5_generator import MD5Generator


class HashCrackerGUI:
    """Interfaz gráfica para el crackeo de hashes MD5"""
    def __init__(self, root):
        self.root = root
        self.root.title("Hash Cracker — Offline")
        self.root.geometry("950x1000")
        self.root.resizable(True, True)

        # Variables compartidas
        self.hashes = []
        self.hashes_file_path = None
        self.cracker = None
        self.crack_thread = None

        # Variables modo diccionario
        self.wordlist_path = None

        # Variables testing
        self.testing_results = {}
        self.md5_gen = MD5Generator()

        # Estilo
        style = ttk.Style()
        style.theme_use('clam')

        # 1. FRAME HASHES (GLOBAL - arriba)
        self.frame_hashes = ttk.LabelFrame(root, text=" 📁 HASHES MD5 ", padding=10)
        self.frame_hashes.pack(side="top", fill="x", padx=10, pady=(10, 0))

        ttk.Button(self.frame_hashes, text="Cargar Hashes (.txt)",
                   command=self.load_hashes).pack(side="left", padx=5)
        self.label_hashes = ttk.Label(self.frame_hashes, text="❌ Ninguno", foreground="red")
        self.label_hashes.pack(side="left", padx=20)

        # 5. FRAME BOTONES (GLOBAL - fondo)
        self.frame_buttons = ttk.Frame(root)
        self.frame_buttons.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        self.btn_start = ttk.Button(self.frame_buttons, text="▶️ INICIAR", command=self.start_crack)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(self.frame_buttons, text="⏹️ PARAR", command=self.stop_crack, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.btn_copy = ttk.Button(self.frame_buttons, text="📋 COPIAR", command=self.copy_results_to_clipboard)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_export = ttk.Button(self.frame_buttons, text="💾 EXPORTAR CSV", command=self.export_csv)
        self.btn_export.pack(side="left", padx=5)

        self.btn_clear = ttk.Button(self.frame_buttons, text="🗑️ LIMPIAR TODO", command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)

        # 4. FRAME PROGRESO (GLOBAL - encima de botones)
        self.frame_progress = ttk.LabelFrame(root, text=" ⏳ PROGRESO ", padding=8)
        self.frame_progress.pack(side="bottom", fill="x", padx=10, pady=(0, 5))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame_progress, mode="determinate",
            variable=self.progress_var
        )
        self.progress_bar.pack(fill="x", pady=3)

        self.label_status = ttk.Label(
            self.frame_progress,
            text="Listo",
            foreground="blue"
        )
        self.label_status.pack(anchor="w")

        # 2. NOTEBOOK: Pestañas (CENTRO-ARRIBA)
        self.notebook = ttk.Notebook(root)
        # Por defecto es compacto en Diccionario/Fuerza Bruta
        self.notebook.pack(side="top", fill="x", expand=False, padx=10, pady=5)

        # Pestañas
        self.tab_dict = ttk.Frame(self.notebook, padding=2)
        self.notebook.add(self.tab_dict, text="  📖 Diccionario  ")
        self._build_tab_diccionario()

        self.tab_brute = ttk.Frame(self.notebook, padding=2)
        self.notebook.add(self.tab_brute, text="  💪 Fuerza Bruta  ")
        self._build_tab_fuerza_bruta()

        self.tab_testing = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_testing, text="  🧪 Testing  ")
        self._build_tab_testing()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # 3. FRAME RESULTADOS (GLOBAL - CENTRAL EXPANDIBLE)
        self.frame_results = ttk.LabelFrame(root, text=" � RESULTADOS ", padding=10)
        self.frame_results.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5))

        self.tree = ttk.Treeview(
            self.frame_results,
            columns=("hash", "password", "metodo"),
            height=18,
            show="headings"
        )
        self.tree.column("hash", width=320, anchor="w")
        self.tree.column("password", width=280, anchor="w")
        self.tree.column("metodo", width=120, anchor="center")
        self.tree.heading("hash", text="MD5 Hash")
        self.tree.heading("password", text="Contraseña")
        self.tree.heading("metodo", text="Método")

        scrollbar = ttk.Scrollbar(self.frame_results, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ─────────────────────────────────────────────
    # PESTAÑA 1: DICCIONARIO
    # ─────────────────────────────────────────────
    def _build_tab_diccionario(self):
        """Configura la pestaña de diccionario"""
        frame_config = ttk.LabelFrame(self.tab_dict, text=" ⚙️ CONFIGURACIÓN ", padding=5)
        frame_config.pack(fill="x", padx=0, pady=(0, 2))
        
        ttk.Button(frame_config, text="Cargar Diccionario (.txt)",
                   command=self.load_wordlist).pack(side="left", padx=5)
        self.label_wordlist = ttk.Label(frame_config, text="❌ Ninguno", foreground="red")
        self.label_wordlist.pack(side="left", padx=20)

    # ─────────────────────────────────────────────
    # PESTAÑA 2: FUERZA BRUTA
    # ─────────────────────────────────────────────
    def _build_tab_fuerza_bruta(self):
        """Configura la pestaña de fuerza bruta"""
        # Fila 1: longitud máxima
        row1 = ttk.Frame(self.tab_brute)
        row1.pack(fill="x", pady=2)

        ttk.Label(row1, text="Longitud máxima:").pack(side="left", padx=5)
        self.var_maxlen = tk.IntVar(value=4)
        spin = ttk.Spinbox(row1, from_=1, to=8, width=5, textvariable=self.var_maxlen)
        spin.pack(side="left", padx=5)

        # Fila 2: charset
        row2 = ttk.Frame(self.tab_brute)
        row2.pack(fill="x", pady=2)

        ttk.Label(row2, text="Caracteres a usar:").pack(side="left", padx=5)

        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=False)
        self.var_digits = tk.BooleanVar(value=False)
        self.var_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(row2, text="a-z", variable=self.var_lower).pack(side="left", padx=4)
        ttk.Checkbutton(row2, text="A-Z", variable=self.var_upper).pack(side="left", padx=4)
        ttk.Checkbutton(row2, text="0-9", variable=self.var_digits).pack(side="left", padx=4)
        ttk.Checkbutton(row2, text="!@#...", variable=self.var_symbols).pack(side="left", padx=4)

        # Fila 3: charset personalizado
        row3 = ttk.Frame(self.tab_brute)
        row3.pack(fill="x", pady=2)

        ttk.Label(row3, text="Charset personalizado:").pack(side="left", padx=5)
        self.var_custom_charset = tk.StringVar()
        ttk.Entry(row3, textvariable=self.var_custom_charset, width=30).pack(side="left", padx=5)

        # Fila 4: estimación
        row4 = ttk.Frame(self.tab_brute)
        row4.pack(fill="x", pady=2)
        self.label_estimacion = ttk.Label(row4, text="", foreground="gray")
        self.label_estimacion.pack(side="left", padx=5)

        # Traces para actualización
        for var in [self.var_lower, self.var_upper, self.var_digits, self.var_symbols, self.var_maxlen]:
            var.trace_add("write", lambda *_: self._update_estimacion())
        self.var_custom_charset.trace_add("write", lambda *_: self._update_estimacion())
        self._update_estimacion()

    def _build_charset(self):
        custom = self.var_custom_charset.get().strip()
        if custom: return custom
        charset = ""
        if self.var_lower.get(): charset += "abcdefghijklmnopqrstuvwxyz"
        if self.var_upper.get(): charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.var_digits.get(): charset += "0123456789"
        if self.var_symbols.get(): charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return charset

    def _update_estimacion(self):
        try:
            charset = self._build_charset()
            if not charset:
                self.label_estimacion.config(text="Selecciona caracteres")
                return
            maxlen = self.var_maxlen.get()
            total = sum(len(charset) ** l for l in range(1, maxlen + 1))
            txt = f"Total de combinaciones: {total:,}"
            self.label_estimacion.config(text=txt, foreground="gray")
        except: pass

    # ─────────────────────────────────────────────
    # PESTAÑA 3: TESTING
    # ─────────────────────────────────────────────
    def _build_tab_testing(self):
        paned = ttk.PanedWindow(self.tab_testing, orient="horizontal")
        paned.pack(fill="both", expand=True)
        
        left = ttk.Frame(paned); right = ttk.Frame(paned)
        paned.add(left, weight=3); paned.add(right, weight=2)

        f_in = ttk.LabelFrame(left, text=" ✍️ PALABRAS ", padding=10)
        f_in.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_passwords = tk.Text(f_in, height=5, width=30)
        self.text_passwords.pack(fill="both", expand=True)
        
        btns = ttk.Frame(f_in)
        btns.pack(fill="x", pady=5)
        ttk.Button(btns, text="🔨 Generar", command=self.generate_md5s).pack(side="left", padx=2)
        ttk.Button(btns, text="📋 Copiar", command=self.copy_md5s).pack(side="left", padx=2)

        f_sim = ttk.LabelFrame(right, text=" 🧪 SIMULACIÓN ", padding=10)
        f_sim.pack(fill="both", expand=True, padx=5, pady=5)
        self.label_sim_info = ttk.Label(f_sim, text="Escribe palabras y genera...", wraplength=150)
        self.label_sim_info.pack(pady=5)
        self.sim_result_var = tk.StringVar(value="-")
        ttk.Label(f_sim, text="ETA Brute Force:").pack()
        ttk.Label(f_sim, textvariable=self.sim_result_var, foreground="blue").pack()
        
        ttk.Button(f_sim, text="➕ A Hashes", command=self.add_to_hashes).pack(fill="x", pady=2)
        ttk.Button(f_sim, text="📖 A Diccionario", command=self.add_to_wordlist).pack(fill="x", pady=2)

        f_res = ttk.LabelFrame(self.tab_testing, text=" 📊 HASHES GENERADOS ", padding=5)
        f_res.pack(fill="both", expand=True, pady=5)
        
        self.tree_testing = ttk.Treeview(f_res, columns=("p", "m", "l"), height=6, show="headings")
        self.tree_testing.heading("p", text="Palabra")
        self.tree_testing.heading("m", text="MD5 Hash")
        self.tree_testing.heading("l", text="Long.")
        self.tree_testing.column("p", width=120, anchor="w")
        self.tree_testing.column("m", width=320, anchor="w")
        self.tree_testing.column("l", width=60, anchor="center")
        
        scroll_test = ttk.Scrollbar(f_res, orient="vertical", command=self.tree_testing.yview)
        self.tree_testing.configure(yscroll=scroll_test.set)
        
        self.tree_testing.pack(side="left", fill="both", expand=True)
        scroll_test.pack(side="right", fill="y")
        
        self.tree_testing.bind("<<TreeviewSelect>>", self.on_testing_select)

    def on_tab_change(self, event):
        """Maneja el cambio de pestañas para ocultar/mostrar resultados globales"""
        try:
            tab_index = self.notebook.index(self.notebook.select())
            
            if tab_index == 2:
                # PESTAÑA TESTING: Ocultar resultados globales y expandir notebook
                self.frame_results.pack_forget()
                # Quitamos restricción de altura para que el notebook crezca en Testing
                self.notebook.configure(height=0) 
                self.notebook.pack(side="top", fill="both", expand=True, padx=10, pady=5, after=self.frame_hashes)
            else:
                # PESTAÑAS DICCIONARIO/BRUTE: Notebook MUY compacto y resultados globales toman TODO el resto
                # Forzamos una altura pequeña para que no desperdicie espacio
                self.notebook.configure(height=120) 
                self.notebook.pack(side="top", fill="x", expand=False, padx=10, pady=5, after=self.frame_hashes)
                self.frame_results.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5), after=self.notebook)
        except:
            pass

    # ─────────────────────────────────────────────
    # FUNCIONES CARGA / CONTROL
    # ─────────────────────────────────────────────
    def load_hashes(self):
        path = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])
        if path:
            self.hashes_file_path = path
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                self.hashes = [l.strip() for l in f if l.strip()]
            self.label_hashes.config(text=f"✅ {len(self.hashes)} hashes", foreground="green")

    def load_wordlist(self):
        path = filedialog.askopenfilename(filetypes=[("TXT", "*.txt")])
        if path:
            self.wordlist_path = path
            self.label_wordlist.config(text=f"✅ {os.path.basename(path)}", foreground="green")

    def start_crack(self):
        if not self.hashes:
            messagebox.showerror("Error", "Carga hashes primero")
            return
        
        try:
            tab_index = self.notebook.index(self.notebook.select())
        except: return

        # LIMPIAR RESULTADOS ANTERIORES AUTOMÁTICAMENTE
        self.tree.delete(*self.tree.get_children())

        if tab_index == 0:
            if not self.wordlist_path:
                messagebox.showerror("Error", "Carga diccionario")
                return
            self.cracker = MD5Cracker(self.hashes, self.wordlist_path)
            metodo = "Diccionario"
        elif tab_index == 1:
            charset = self._build_charset()
            if not charset: return
            self.cracker = BruteForceCracker(self.hashes, charset, self.var_maxlen.get())
            metodo = "Fuerza Bruta"
        else:
            return

        self.cracker.set_progress_callback(self.update_progress)
        self.btn_start.config(state="disabled"); self.btn_stop.config(state="normal")
        self.progress_var.set(0)
        self.label_status.config(text=f"⏳ Crackeando ({metodo})...", foreground="orange")
        
        self.crack_thread = threading.Thread(target=self._crack_worker, args=(metodo,), daemon=True)
        self.crack_thread.start()

    def _crack_worker(self, metodo):
        try:
            results = self.cracker.crack(num_threads=4)
            self.root.after(0, lambda: self.display_results(results, metodo))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def update_progress(self, proc, total, found):
        if total > 0:
            pct = (proc / total) * 100
            self.progress_var.set(pct)
            self.label_status.config(text=f"⏳ {proc:,}/{total:,} | Encontrados: {found}")
            self.root.update_idletasks()

    def display_results(self, results, metodo):
        ya_en_tabla = {self.tree.item(i, 'values')[0] for i in self.tree.get_children()}
        for h, p in results.items():
            if h not in ya_en_tabla: self.tree.insert("", "end", values=(h, p, metodo))
        self.label_status.config(text=f"✅ COMPLETADO | Total: {len(self.tree.get_children())}", foreground="green")
        self.btn_start.config(state="normal"); self.btn_stop.config(state="disabled")

    def stop_crack(self):
        if self.cracker: self.cracker.stop()
        self.label_status.config(text="⏹️ Parado", foreground="red")
        self.btn_start.config(state="normal"); self.btn_stop.config(state="disabled")

    def clear_all(self):
        self.hashes = []; self.wordlist_path = None; self.hashes_file_path = None
        self.tree.delete(*self.tree.get_children())
        self.label_hashes.config(text="❌ Ninguno", foreground="red")
        self.label_wordlist.config(text="❌ Ninguno", foreground="red")
        self.label_status.config(text="Listo"); self.progress_var.set(0)

    def copy_results_to_clipboard(self):
        items = self.tree.get_children()
        if not items: return
        txt = "\n".join([f"{self.tree.item(i, 'values')[1]}:{self.tree.item(i, 'values')[0]}" for i in items])
        self.root.clipboard_clear(); self.root.clipboard_append(txt); self.root.update()
        messagebox.showinfo("OK", "Copiado!")

    def export_csv(self):
        items = self.tree.get_children()
        if not items: return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("Hash,Pass,Metodo\n")
                for i in items:
                    v = self.tree.item(i, 'values')
                    f.write(f'"{v[0]}","{v[1]}","{v[2]}"\n')

    # Testing Methods
    def generate_md5s(self):
        txt = self.text_passwords.get("1.0", tk.END).strip()
        if not txt: return
        
        # Limpiar tabla anterior
        for i in self.tree_testing.get_children(): self.tree_testing.delete(i)
        
        self.testing_results = self.md5_gen.generate_from_text(txt)
        
        # Poblar la tabla de Testing
        for h, p in self.testing_results.items():
            self.tree_testing.insert("", "end", values=(p, h, len(p)))

        # Actualizamos la simulación con la primera palabra generada
        if self.testing_results:
            first_hash = list(self.testing_results.keys())[0]
            first_word = self.testing_results[first_hash]
            self._update_sim_from_word(first_word)
        messagebox.showinfo("🧪 Testing", f"Se han generado {len(self.testing_results)} hashes MD5.")

    def on_testing_select(self, e):
        """Permite actualizar la simulación al seleccionar una palabra de la lista generada"""
        sel = self.tree_testing.selection()
        if not sel: return
        item = self.tree_testing.item(sel[0])
        p = item['values'][0]
        self._update_sim_from_word(p)

    def _update_sim_from_word(self, word):
        l = len(str(word))
        cs = len(self._build_charset())
        if cs == 0: 
            self.sim_result_var.set("Selecciona charset!")
            return
            
        total_prev = sum(cs ** i for i in range(1, l))
        # Velocidad estimada: 500k hashes/segundo (muy conservador)
        sec = total_prev / 500000
        
        if sec < 1: t = "< 1s"
        elif sec < 60: t = f"~{sec:.1f}s"
        elif sec < 3600: t = f"~{sec/60:.1f}m"
        else: t = f"~{sec/3600:.1f}h"
        
        self.sim_result_var.set(t)
        self.label_sim_info.config(text=f"Palabra: '{word}'\nCharset: {cs} chars")

    def add_to_hashes(self):
        """Añade los hashes generados a la lista de objetivos principal y al archivo cargado"""
        if not self.testing_results:
            messagebox.showwarning("Aviso", "Genera algunos hashes primero")
            return
        
        # Si no hay archivo cargado, preguntamos si quiere crear uno
        if not self.hashes_file_path:
            if messagebox.askyesno("Hashes", "No has cargado ningún archivo de hashes. ¿Quieres crear uno nuevo?"):
                path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
                if path:
                    self.hashes_file_path = path
                    self.hashes = [] # Empezamos de cero si es archivo nuevo
                else:
                    return
            else:
                return

        # Añadimos a la lista en memoria y al archivo
        nuevos_hashes = []
        count = 0
        for h in self.testing_results.keys():
            h_clean = h.lower().strip()
            if h_clean not in self.hashes:
                self.hashes.append(h_clean)
                nuevos_hashes.append(h_clean)
                count += 1
        
        if count > 0:
            try:
                # Verificar si el archivo termina en nueva línea
                prefix = ""
                if os.path.exists(self.hashes_file_path) and os.path.getsize(self.hashes_file_path) > 0:
                    with open(self.hashes_file_path, 'rb') as f:
                        f.seek(-1, os.SEEK_END)
                        if f.read(1) != b'\n':
                            prefix = "\n"
                
                # Escribimos en el archivo (.txt)
                with open(self.hashes_file_path, 'a', encoding='utf-8') as f:
                    if prefix: f.write(prefix)
                    for h in nuevos_hashes:
                        f.write(h + '\n')
                
                self.label_hashes.config(text=f"✅ {len(self.hashes)} hashes", foreground="green")
                messagebox.showinfo("Éxito", f"Se han añadido {count} hashes nuevos a:\n{os.path.basename(self.hashes_file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo escribir en el archivo: {e}")
        else:
            messagebox.showinfo("Aviso", "Todos los hashes ya estaban en la lista.")

    def add_to_wordlist(self):
        """Añade las palabras del testing al diccionario cargado"""
        if not self.testing_results:
            messagebox.showwarning("Aviso", "Genera algunas palabras primero")
            return
            
        if not self.wordlist_path:
            messagebox.showwarning("Aviso", "No hay ningún diccionario cargado")
            return
            
        try:
            # Verificar si el archivo termina en nueva línea
            prefix = ""
            if os.path.exists(self.wordlist_path) and os.path.getsize(self.wordlist_path) > 0:
                with open(self.wordlist_path, 'rb') as f:
                    f.seek(-1, os.SEEK_END)
                    if f.read(1) != b'\n':
                        prefix = "\n"
            
            with open(self.wordlist_path, 'a', encoding='utf-8') as f:
                if prefix: f.write(prefix)
                for p in self.testing_results.values():
                    f.write(p + '\n')
            messagebox.showinfo("Éxito", "Palabras añadidas al diccionario")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo escribir en el archivo: {e}")

    def copy_md5s(self):
        if not self.testing_results: return
        txt = "\n".join(self.testing_results.keys())
        self.root.clipboard_clear(); self.root.clipboard_append(txt); self.root.update()
        messagebox.showinfo("🧪 Testing", "Hashes copiados al portapapeles.")
