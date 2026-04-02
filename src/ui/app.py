# src/ui/app.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from src.core.cracker import MD5Cracker

class HashCrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hash Cracker — Offline")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Variables
        self.hashes = []
        self.wordlist_path = None
        self.cracker = None
        self.crack_thread = None
        
        # Estilos (compatible con PCs viejas)
        style = ttk.Style()
        style.theme_use('clam')  # tema clásico, ligero
        
        # ===== FRAME SUPERIOR: Carga de archivos =====
        frame_load = ttk.LabelFrame(root, text=" 📁 CARGAR ARCHIVOS ", padding=10)
        frame_load.pack(fill="x", padx=10, pady=10)
        
        # Botón cargar hashes
        ttk.Button(frame_load, text="Cargar Hashes (MD5)", 
                  command=self.load_hashes).pack(side="left", padx=5)
        self.label_hashes = ttk.Label(frame_load, text="❌ Ninguno", foreground="red")
        self.label_hashes.pack(side="left", padx=20)
        
        # Botón cargar wordlist
        ttk.Button(frame_load, text="Cargar Diccionario", 
                  command=self.load_wordlist).pack(side="left", padx=5)
        self.label_wordlist = ttk.Label(frame_load, text="❌ Ninguno", foreground="red")
        self.label_wordlist.pack(side="left", padx=20)
        
        # ===== FRAME CENTRAL: Tabla de resultados =====
        frame_results = ttk.LabelFrame(root, text=" 🔐 RESULTADOS ", padding=10)
        frame_results.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear Treeview con scroll
        self.tree = ttk.Treeview(
            frame_results,
            columns=("hash", "password"),
            height=20,
            show="headings"
        )
        
        self.tree.column("hash", width=350, anchor="w")
        self.tree.column("password", width=350, anchor="w")
        self.tree.heading("hash", text="MD5 Hash")
        self.tree.heading("password", text="Contraseña")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_results, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== FRAME PROGRESO =====
        frame_progress = ttk.LabelFrame(root, text=" ⏳ PROGRESO ", padding=10)
        frame_progress.pack(fill="x", padx=10, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            frame_progress,
            mode="determinate",
            variable=self.progress_var,
            length=400
        )
        self.progress_bar.pack(fill="x", pady=5)
        
        self.label_status = ttk.Label(
            frame_progress,
            text="Listo | Hashes: 0 | Encontrados: 0 | Procesados: 0",
            foreground="blue"
        )
        self.label_status.pack(anchor="w")
        
        # ===== FRAME BOTONES =====
        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(fill="x", padx=10, pady=10)
        
        self.btn_start = ttk.Button(
            frame_buttons,
            text="▶️ INICIAR",
            command=self.start_crack
        )
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(
            frame_buttons,
            text="⏹️ PARAR",
            command=self.stop_crack,
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_export = ttk.Button(
            frame_buttons,
            text="💾 EXPORTAR CSV",
            command=self.export_csv
        )
        self.btn_export.pack(side="left", padx=5)
        
        self.btn_clear = ttk.Button(
            frame_buttons,
            text="🗑️ LIMPIAR",
            command=self.clear_all
        )
        self.btn_clear.pack(side="left", padx=5)
    
    def load_hashes(self):
        """Cargar archivo con hashes"""
        path = filedialog.askopenfilename(
            title="Selecciona archivo con hashes MD5",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.hashes = [line.strip() for line in f if line.strip()]
                
                if self.hashes:
                    self.label_hashes.config(
                        text=f"✅ {len(self.hashes)} hashes",
                        foreground="green"
                    )
                else:
                    messagebox.showwarning("Aviso", "Archivo vacío")
                    self.label_hashes.config(text="❌ Vacío", foreground="red")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer: {e}")
    
    def load_wordlist(self):
        """Cargar diccionario"""
        path = filedialog.askopenfilename(
            title="Selecciona diccionario",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if path:
            try:
                # Verificar que el archivo existe y tiene contenido
                if os.path.getsize(path) > 0:
                    self.wordlist_path = path
                    filename = os.path.basename(path)
                    self.label_wordlist.config(
                        text=f"✅ {filename}",
                        foreground="green"
                    )
                else:
                    messagebox.showwarning("Aviso", "Diccionario vacío")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer: {e}")
    
    def start_crack(self):
        """Iniciar cracking"""
        if not self.hashes:
            messagebox.showerror("Error", "Carga hashes primero")
            return
        if not self.wordlist_path:
            messagebox.showerror("Error", "Carga un diccionario")
            return
        
        # Desactivar botones
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.progress_var.set(0)
        self.label_status.config(text="⏳ Iniciando...", foreground="orange")
        
        # Crear cracker
        self.cracker = MD5Cracker(self.hashes, self.wordlist_path)
        self.cracker.set_progress_callback(self.update_progress)
        
        # Lanzar en thread
        self.crack_thread = threading.Thread(target=self._crack_worker, daemon=True)
        self.crack_thread.start()
    
    def _crack_worker(self):
        """Worker en thread separado"""
        try:
            results = self.cracker.crack(num_threads=2)  # 2 threads para máquinas viejas
            # Actualizar UI desde el thread principal
            self.root.after(0, lambda: self.display_results(results))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def update_progress(self, processed, total, found):
        """Callback de progreso (llamado desde worker)"""
        if total > 0:
            pct = (processed / total) * 100
            self.progress_var.set(pct)
            self.label_status.config(
                text=f"⏳ Procesados: {processed}/{total} | Encontrados: {found}",
                foreground="blue"
            )
            self.root.update_idletasks()
    
    def display_results(self, results):
        """Mostrar resultados en tabla"""
        self.tree.delete(*self.tree.get_children())
        
        for hash_val, password in sorted(results.items()):
            self.tree.insert("", "end", values=(hash_val, password))
        
        total = len(self.hashes)
        found = len(results)
        
        self.label_status.config(
            text=f"✅ COMPLETADO | Hashes: {total} | Encontrados: {found}/{total} ({found*100//total if total else 0}%)",
            foreground="green"
        )
        
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
    
    def stop_crack(self):
        """Detener cracking"""
        if self.cracker:
            self.cracker.stop()
        self.label_status.config(text="⏹️ Detenido por usuario", foreground="red")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
    
    def export_csv(self):
        """Exportar resultados a CSV"""
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
                    f.write("MD5 Hash,Contraseña\n")
                    for item in items:
                        values = self.tree.item(item, 'values')
                        f.write(f'"{values[0]}","{values[1]}"\n')
                messagebox.showinfo("Éxito", f"Exportado a:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {e}")
    
    def clear_all(self):
        """Limpiar todo"""
        self.hashes = []
        self.wordlist_path = None
        self.tree.delete(*self.tree.get_children())
        self.label_hashes.config(text="❌ Ninguno", foreground="red")
        self.label_wordlist.config(text="❌ Ninguno", foreground="red")
        self.label_status.config(text="Listo", foreground="blue")
        self.progress_var.set(0)