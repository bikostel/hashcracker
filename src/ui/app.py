# src/ui/app.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from src.core.cracker import MD5Cracker, BruteForceCracker


class HashCrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hash Cracker — Offline")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variables compartidas
        self.hashes = []
        self.cracker = None
        self.crack_thread = None

        # Variables modo diccionario
        self.wordlist_path = None

        # Estilo
        style = ttk.Style()
        style.theme_use('clam')

        # ===== FRAME HASHES (compartido por ambas pestañas) =====
        frame_hashes = ttk.LabelFrame(root, text=" 📁 HASHES MD5 ", padding=10)
        frame_hashes.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Button(frame_hashes, text="Cargar Hashes (.txt)",
                   command=self.load_hashes).pack(side="left", padx=5)
        self.label_hashes = ttk.Label(frame_hashes, text="❌ Ninguno", foreground="red")
        self.label_hashes.pack(side="left", padx=20)

        # ===== NOTEBOOK: Pestañas =====
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=False, padx=10, pady=10)

        # Pestaña 1: Diccionario
        self.tab_dict = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_dict, text="  📖 Diccionario  ")
        self._build_tab_diccionario()

        # Pestaña 2: Fuerza Bruta
        self.tab_brute = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_brute, text="  💪 Fuerza Bruta  ")
        self._build_tab_fuerza_bruta()

        # ===== FRAME RESULTADOS (compartido) =====
        frame_results = ttk.LabelFrame(root, text=" 🔐 RESULTADOS ", padding=10)
        frame_results.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self.tree = ttk.Treeview(
            frame_results,
            columns=("hash", "password", "metodo"),
            height=10,
            show="headings"
        )
        self.tree.column("hash", width=320, anchor="w")
        self.tree.column("password", width=280, anchor="w")
        self.tree.column("metodo", width=120, anchor="center")
        self.tree.heading("hash", text="MD5 Hash")
        self.tree.heading("password", text="Contraseña")
        self.tree.heading("metodo", text="Método")

        scrollbar = ttk.Scrollbar(frame_results, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== FRAME PROGRESO (compartido) =====
        frame_progress = ttk.LabelFrame(root, text=" ⏳ PROGRESO ", padding=8)
        frame_progress.pack(fill="x", padx=10, pady=(0, 5))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            frame_progress, mode="determinate",
            variable=self.progress_var
        )
        self.progress_bar.pack(fill="x", pady=3)

        self.label_status = ttk.Label(
            frame_progress,
            text="Listo",
            foreground="blue"
        )
        self.label_status.pack(anchor="w")

        # ===== FRAME BOTONES (compartido) =====
        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_start = ttk.Button(frame_buttons, text="▶️ INICIAR", command=self.start_crack)
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(frame_buttons, text="⏹️ PARAR", command=self.stop_crack, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.btn_export = ttk.Button(frame_buttons, text="💾 EXPORTAR CSV", command=self.export_csv)
        self.btn_export.pack(side="left", padx=5)

        self.btn_clear = ttk.Button(frame_buttons, text="🗑️ LIMPIAR", command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)

    # ─────────────────────────────────────────────
    # PESTAÑA 1: DICCIONARIO
    # ─────────────────────────────────────────────
    def _build_tab_diccionario(self):
        ttk.Button(self.tab_dict, text="Cargar Diccionario (.txt)",
                   command=self.load_wordlist).pack(side="left", padx=5)
        self.label_wordlist = ttk.Label(self.tab_dict, text="❌ Ninguno", foreground="red")
        self.label_wordlist.pack(side="left", padx=10)

    # ─────────────────────────────────────────────
    # PESTAÑA 2: FUERZA BRUTA
    # ─────────────────────────────────────────────
    def _build_tab_fuerza_bruta(self):
        # Fila 1: longitud máxima
        row1 = ttk.Frame(self.tab_brute)
        row1.pack(fill="x", pady=4)

        ttk.Label(row1, text="Longitud máxima:").pack(side="left", padx=5)
        self.var_maxlen = tk.IntVar(value=4)
        spin = ttk.Spinbox(row1, from_=1, to=8, width=5, textvariable=self.var_maxlen)
        spin.pack(side="left", padx=5)

        # Aviso de tiempo estimado
        ttk.Label(
            row1,
            text="⚠️  Más de 5 caracteres puede tardar horas en PCs lentas",
            foreground="orange"
        ).pack(side="left", padx=15)

        # Fila 2: charset
        row2 = ttk.Frame(self.tab_brute)
        row2.pack(fill="x", pady=4)

        ttk.Label(row2, text="Caracteres a usar:").pack(side="left", padx=5)

        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=False)
        self.var_digits = tk.BooleanVar(value=False)
        self.var_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(row2, text="a-z", variable=self.var_lower).pack(side="left", padx=4)
        ttk.Checkbutton(row2, text="A-Z", variable=self.var_upper).pack(side="left", padx=4)
        ttk.Checkbutton(row2, text="0-9", variable=self.var_digits).pack(side="left", padx=4)
        ttk.Checkbutton(row2, text="!@#...", variable=self.var_symbols).pack(side="left", padx=4)

        # Fila 3: charset personalizado opcional
        row3 = ttk.Frame(self.tab_brute)
        row3.pack(fill="x", pady=4)

        ttk.Label(row3, text="Charset personalizado (opcional):").pack(side="left", padx=5)
        self.var_custom_charset = tk.StringVar()
        ttk.Entry(row3, textvariable=self.var_custom_charset, width=30).pack(side="left", padx=5)
        ttk.Label(row3, text="(deja vacío para usar las casillas de arriba)", foreground="gray").pack(side="left")

        # Fila 4: estimación en tiempo real
        row4 = ttk.Frame(self.tab_brute)
        row4.pack(fill="x", pady=4)
        self.label_estimacion = ttk.Label(row4, text="", foreground="gray")
        self.label_estimacion.pack(side="left", padx=5)

        # Bindings para actualizar estimación al cambiar parámetros
        for var in [self.var_lower, self.var_upper, self.var_digits,
                    self.var_symbols, self.var_maxlen]:
            var.trace_add("write", lambda *_: self._update_estimacion())
        self.var_custom_charset.trace_add("write", lambda *_: self._update_estimacion())

        self._update_estimacion()

    def _build_charset(self):
        """Construye el charset según las opciones marcadas."""
        custom = self.var_custom_charset.get().strip()
        if custom:
            return custom

        charset = ""
        if self.var_lower.get():
            charset += "abcdefghijklmnopqrstuvwxyz"
        if self.var_upper.get():
            charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.var_digits.get():
            charset += "0123456789"
        if self.var_symbols.get():
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return charset

    def _update_estimacion(self):
        """Muestra cuántas combinaciones se van a generar."""
        try:
            charset = self._build_charset()
            if not charset:
                self.label_estimacion.config(text="Selecciona al menos un tipo de caracter")
                return
            maxlen = self.var_maxlen.get()
            total = sum(len(charset) ** l for l in range(1, maxlen + 1))
            if total < 1_000_000:
                txt = f"~{total:,} combinaciones  (rápido ✅)"
                color = "green"
            elif total < 50_000_000:
                txt = f"~{total:,} combinaciones  (puede tardar varios minutos ⚠️)"
                color = "orange"
            else:
                txt = f"~{total:,} combinaciones  (MUY lento en PCs antiguas ❌)"
                color = "red"
            self.label_estimacion.config(text=txt, foreground=color)
        except Exception:
            pass

    # ─────────────────────────────────────────────
    # CARGA DE ARCHIVOS
    # ─────────────────────────────────────────────
    def load_hashes(self):
        path = filedialog.askopenfilename(
            title="Selecciona archivo con hashes MD5",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.hashes = [line.strip() for line in f if line.strip()]
                if self.hashes:
                    self.label_hashes.config(text=f"✅ {len(self.hashes)} hashes", foreground="green")
                else:
                    messagebox.showwarning("Aviso", "Archivo vacío")
                    self.label_hashes.config(text="❌ Vacío", foreground="red")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer: {e}")

    def load_wordlist(self):
        path = filedialog.askopenfilename(
            title="Selecciona diccionario",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if path:
            try:
                if os.path.getsize(path) > 0:
                    self.wordlist_path = path
                    self.label_wordlist.config(
                        text=f"✅ {os.path.basename(path)}", foreground="green"
                    )
                else:
                    messagebox.showwarning("Aviso", "Diccionario vacío")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer: {e}")

    # ─────────────────────────────────────────────
    # CONTROL PRINCIPAL
    # ─────────────────────────────────────────────
    def start_crack(self):
        if not self.hashes:
            messagebox.showerror("Error", "Carga hashes primero")
            return

        tab = self.notebook.index(self.notebook.select())

        if tab == 0:
            # Modo diccionario
            if not self.wordlist_path:
                messagebox.showerror("Error", "Carga un diccionario primero")
                return
            self.cracker = MD5Cracker(self.hashes, self.wordlist_path)
            self.cracker.set_progress_callback(self.update_progress)
            metodo = "Diccionario"

        else:
            # Modo fuerza bruta
            charset = self._build_charset()
            if not charset:
                messagebox.showerror("Error", "Selecciona al menos un tipo de caracter")
                return
            maxlen = self.var_maxlen.get()
            self.cracker = BruteForceCracker(self.hashes, charset=charset, max_length=maxlen)
            self.cracker.set_progress_callback(self.update_progress)
            metodo = "Fuerza Bruta"

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.progress_var.set(0)
        self.label_status.config(text=f"⏳ Iniciando ({metodo})...", foreground="orange")

        self.crack_thread = threading.Thread(
            target=self._crack_worker, args=(metodo,), daemon=True
        )
        self.crack_thread.start()

    def _crack_worker(self, metodo):
        try:
            results = self.cracker.crack(num_threads=2)
            self.root.after(0, lambda: self.display_results(results, metodo))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def update_progress(self, processed, total, found):
        if total > 0:
            pct = (processed / total) * 100
            self.progress_var.set(pct)
            self.label_status.config(
                text=f"⏳ Procesados: {processed:,}/{total:,} | Encontrados: {found}",
                foreground="blue"
            )
            self.root.update_idletasks()

    def display_results(self, results, metodo=""):
        # No borrar resultados anteriores, solo añadir los nuevos
        hashes_ya_en_tabla = {
            self.tree.item(i, 'values')[0] for i in self.tree.get_children()
        }
        for hash_val, password in sorted(results.items()):
            if hash_val not in hashes_ya_en_tabla:
                self.tree.insert("", "end", values=(hash_val, password, metodo))

        total = len(self.hashes)
        found = len(self.tree.get_children())

        self.label_status.config(
            text=f"✅ COMPLETADO | Hashes: {total} | En tabla: {found} | ({found*100//total if total else 0}%)",
            foreground="green"
        )
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def stop_crack(self):
        if self.cracker:
            self.cracker.stop()
        self.label_status.config(text="⏹️ Detenido por usuario", foreground="red")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    # ─────────────────────────────────────────────
    # EXPORTAR / LIMPIAR
    # ─────────────────────────────────────────────
    def export_csv(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Aviso", "No hay resultados para exportar")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("MD5 Hash,Contraseña,Método\n")
                    for item in items:
                        v = self.tree.item(item, 'values')
                        f.write(f'"{v[0]}","{v[1]}","{v[2]}"\n')
                messagebox.showinfo("Éxito", f"Exportado a:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def clear_all(self):
        self.hashes = []
        self.wordlist_path = None
        self.tree.delete(*self.tree.get_children())
        self.label_hashes.config(text="❌ Ninguno", foreground="red")
        self.label_wordlist.config(text="❌ Ninguno", foreground="red")
        self.label_status.config(text="Listo", foreground="blue")
        self.progress_var.set(0)