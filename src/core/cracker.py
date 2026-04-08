# src/core/cracker.py
import hashlib
import threading
from queue import Queue, Empty
import itertools
import string

class MD5Cracker:

    def __init__(self, target_hashes, wordlist_path):

        self.target_hashes = {h.lower().strip() for h in target_hashes if h.strip()}
        self.wordlist_path = wordlist_path
        self.results = {}  # {hash_encontrado: password}
        self.stop_flag = False
        self.progress_callback = None
        self.total_lines = 0
        self.processed = 0
        self.found = 0
    
    def set_progress_callback(self, callback):

        self.progress_callback = callback
    
    def count_lines(self):
   
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.total_lines = sum(1 for _ in f)
            return self.total_lines
        except Exception as e:
            print(f"Error contando líneas: {e}")
            return 0
    
    def crack(self, num_threads=2):
    
        self.stop_flag = False
        self.processed = 0
        self.found = 0
        
        # Paso 1: Contar líneas
        self.count_lines()
        if self.total_lines == 0:
            raise ValueError("Wordlist vacía o no accesible")
        
        # Paso 2: Crear cola de trabajo
        # maxsize=1000 → guarda máximo 1000 palabras en memoria a la vez
        # Si el lector es más rápido, espera. Si los workers son más rápidos,
        # el lector sigue. Esto balancea todo.
        work_queue = Queue(maxsize=1000)
        
        # Paso 3: Crear thread lector
        reader_thread = threading.Thread(
            target=self._reader_worker,
            args=(work_queue,),
            daemon=True  # Si la app cierra, este thread muere automáticamente
        )
        reader_thread.start()
        
        # Paso 4: Crear threads workers (procesadores de hashes)
        worker_threads = []
        for i in range(num_threads):
            t = threading.Thread(
                target=self._hash_worker,
                args=(work_queue,),
                daemon=True
            )
            t.start()
            worker_threads.append(t)
        
        # Paso 5: Esperar a que terminen
        reader_thread.join()  # Espera a que termine de leer el diccionario
        work_queue.join()     # Espera a que se procesen TODAS las palabras
        
        for t in worker_threads:
            t.join(timeout=1)
        
        return self.results
    
    def _reader_worker(self, queue):

        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if self.stop_flag:
                        break
                    word = line.strip()  # Quita espacios en blanco
                    if word:  # Si no está vacía
                        queue.put(word)  # Mete en la cola
        except Exception as e:
            print(f"Error leyendo wordlist: {e}")
    
    def _hash_worker(self, queue):
   
        while not self.stop_flag:
            try:
                # Intenta tomar una palabra de la cola
                # timeout=1 → si no hay nada en 1 segundo, sale del loop
                word = queue.get(timeout=1)
            except Empty:
                # No hay más palabras
                break
            
            try:
                # PASO 1: Calcular MD5 de la palabra
                # hashlib.md5() → crea un objeto hash
                # word.encode('utf-8') → convierte string a bytes
                # .hexdigest() → devuelve el hash en formato hexadecimal
                # Ejemplo: "password" → "5f4dcc3b5aa765d61d8327deb882cf99"
                md5_hash = hashlib.md5(word.encode('utf-8')).hexdigest()
                
                # PASO 2: ¿Este hash coincide con alguno que buscamos?
                # if md5_hash in self.target_hashes:
                #    ↓ Búsqueda ULTRA rápida porque es un conjunto (set)
                if md5_hash in self.target_hashes:
                    # ¡ENCONTRADO!
                    self.results[md5_hash] = word
                    self.found += 1
                
                # PASO 3: Actualizar progreso (cada 100 palabras)
                self.processed += 1
                if self.progress_callback and self.processed % 100 == 0:
                    self.progress_callback(self.processed, self.total_lines, self.found)
                
            except Exception as e:
                print(f"Error procesando palabra: {e}")
            finally:
                # Indica que terminamos de procesar esta palabra
                queue.task_done()
    
    def stop(self):

        self.stop_flag = True


        # ============================================================================
# FUERZA BRUTA: Generar combinaciones y compararlas con hashes objetivo
# ============================================================================

import itertools
import string

class BruteForceCracker:
    def __init__(self, target_hashes, charset='abcdefghijklmnopqrstuvwxyz', max_length=6):
     
        self.target_hashes = {h.lower().strip() for h in target_hashes if h.strip()}
        self.charset = charset
        self.max_length = max_length
        self.results = {}  # {hash: password}
        self.stop_flag = False
        self.progress_callback = None
        self.processed = 0
        self.found = 0
        self.total_combinations = self._calculate_total()
    
    def set_progress_callback(self, callback):
  
        self.progress_callback = callback
    
    def _calculate_total(self):
      
        charset_len = len(self.charset)
        total = 0
        for length in range(1, self.max_length + 1):
            total += charset_len ** length
        return total
    
    def crack(self, num_threads=2):
       
        self.stop_flag = False
        self.processed = 0
        self.found = 0
        
        # Generar y procesar combinaciones de todas las longitudes
        for length in range(1, self.max_length + 1):
            if self.stop_flag:
                break
            
            # itertools.product genera TODAS las combinaciones
            for combination in itertools.product(self.charset, repeat=length):
                if self.stop_flag:
                    break
                
                # Convertir tupla ('a', 'b') a string 'ab'
                word = ''.join(combination)
                
                # Calcular MD5
                md5_hash = hashlib.md5(word.encode('utf-8')).hexdigest()
                
                # ¿Coincide con algún objetivo?
                if md5_hash in self.target_hashes:
                    self.results[md5_hash] = word
                    self.found += 1
                
                # Actualizar progreso cada 10000 combinaciones
                self.processed += 1
                if self.progress_callback and self.processed % 10000 == 0:
                    self.progress_callback(self.processed, self.total_combinations, self.found)
        
        return self.results
    
    def stop(self):
        """Detiene la búsqueda"""
        self.stop_flag = True