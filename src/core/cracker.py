# src/core/cracker.py
import hashlib
import threading
from queue import Queue, Empty
import itertools

class MD5Cracker:
    """Ataque por diccionario para hashes MD5"""

    def __init__(self, target_hashes, wordlist_path):
        self.target_hashes = {h.lower().strip() for h in target_hashes if h.strip()}
        self.wordlist_path = wordlist_path
        self.results = {}  # {hash_encontrado: password}
        self.stop_flag = False
        self.progress_callback = None
        self.total_lines = 0
        self.processed = 0
        self.found = 0
        self.lock = threading.Lock()
    
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
    
    def crack(self, num_threads=4):
        self.stop_flag = False
        self.processed = 0
        self.found = 0
        self.results = {}
        
        # Paso 1: Contar líneas
        self.count_lines()
        if self.total_lines == 0:
            raise ValueError("Wordlist vacía o no accesible")
        
        # Paso 2: Crear cola de trabajo (balanceo)
        work_queue = Queue(maxsize=1000)
        
        # Paso 3: Crear thread lector
        reader_thread = threading.Thread(
            target=self._reader_worker,
            args=(work_queue,),
            daemon=True
        )
        reader_thread.start()
        
        # Paso 4: Crear threads workers
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
        reader_thread.join()
        work_queue.join()
        
        for t in worker_threads:
            t.join(timeout=1)
        
        return self.results
    
    def _reader_worker(self, queue):
        try:
            with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if self.stop_flag:
                        break
                    word = line.strip()
                    if word:
                        queue.put(word)
        except Exception as e:
            print(f"Error leyendo wordlist: {e}")
    
    def _hash_worker(self, queue):
        while not self.stop_flag:
            try:
                word = queue.get(timeout=0.5)
            except Empty:
                break
            
            try:
                md5_hash = hashlib.md5(word.encode('utf-8')).hexdigest()
                
                if md5_hash in self.target_hashes:
                    with self.lock:
                        self.results[md5_hash] = word
                        self.found += 1
                
                with self.lock:
                    self.processed += 1
                    current_processed = self.processed
                    current_found = self.found
                
                if self.progress_callback and current_processed % 100 == 0:
                    self.progress_callback(current_processed, self.total_lines, current_found)
                
            except Exception as e:
                print(f"Error procesando palabra: {e}")
            finally:
                queue.task_done()
    
    def stop(self):
        """Detiene el cracking"""
        self.stop_flag = True


class BruteForceCracker:
    """Ataque de fuerza bruta para hashes MD5 optimizado"""

    def __init__(self, target_hashes, charset='abcdefghijklmnopqrstuvwxyz', max_length=6):
        self.target_hashes = {h.lower().strip() for h in target_hashes if h.strip()}
        self.charset = charset
        self.max_length = max_length
        self.results = {}  # {hash: password}
        self.stop_flag = False
        self.progress_callback = None
        self.processed = 0
        self.found = 0
        self.lock = threading.Lock()
        self.total_combinations = self._calculate_total()
    
    def set_progress_callback(self, callback):
        self.progress_callback = callback
    
    def _calculate_total(self):
        charset_len = len(self.charset)
        total = 0
        for length in range(1, self.max_length + 1):
            total += charset_len ** length
        return total
    
    def crack(self, num_threads=4):
        """Inicia el ataque de fuerza bruta con múltiples hilos de forma más eficiente"""
        self.stop_flag = False
        self.processed = 0
        self.found = 0
        self.results = {}
        
        task_queue = Queue()
        
        # Repartimos las tareas por el primer carácter para cada longitud
        for length in range(1, self.max_length + 1):
            if length == 1:
                # Longitud 1 se procesa en una sola tarea pequeña
                task_queue.put((1, None))
            else:
                # Longitud > 1 se reparte: cada tarea es (longitud, primer_carácter)
                for char in self.charset:
                    task_queue.put((length, char))
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self._brute_worker, args=(task_queue,))
            t.start()
            threads.append(t)
        
        # Bucle de espera para que sea sensible al stop_flag desde el hilo principal
        while any(t.is_alive() for t in threads):
            if self.stop_flag:
                break
            for t in threads:
                t.join(timeout=0.1)
            
        return self.results

    def _brute_worker(self, queue):
        """Worker que genera y prueba combinaciones"""
        while not self.stop_flag:
            try:
                task = queue.get(timeout=0.2)
            except Empty:
                break
                
            length, start_char = task
            
            if length == 1:
                for char in self.charset:
                    if self.stop_flag: break
                    self._check_word(char)
            else:
                # Optimizamos: itertools.product es muy rápido, lo usamos para el resto de la palabra
                for combo in itertools.product(self.charset, repeat=length-1):
                    if self.stop_flag: break
                    word = start_char + "".join(combo)
                    self._check_word(word)
            
            queue.task_done()

    def _check_word(self, word):
        """Calcula MD5 y compara (sin bloqueos innecesarios para velocidad)"""
        md5_hash = hashlib.md5(word.encode('utf-8')).hexdigest()
        
        if md5_hash in self.target_hashes:
            with self.lock:
                self.results[md5_hash] = word
                self.found += 1
            
        # Actualizamos el contador global de forma atómica
        with self.lock:
            self.processed += 1
            current_processed = self.processed
            current_found = self.found
            
        # El callback de progreso solo cada 10.000 para no saturar la UI
        if self.progress_callback and current_processed % 10000 == 0:
            self.progress_callback(current_processed, self.total_combinations, current_found)

    def stop(self):
        """Detiene el cracking de forma inmediata"""
        self.stop_flag = True
