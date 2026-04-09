# src/core/md5_generator.py
import hashlib

class MD5Generator:
    """Generador de hashes MD5 desde palabras"""
    
    def __init__(self):
        self.results = {}
    
    def generate_from_text(self, text):
        """
        Genera MD5s desde texto (una palabra por línea)
        
        Entrada: 
            text (str): palabras separadas por saltos de línea
        
        Salida:
            dict: {md5_hash: password}
        """
        self.results = {}
        
        for password in text.split('\n'):
            password = password.strip()
            if password:  # Si no está vacía
                md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
                self.results[md5_hash] = password
        
        return self.results
    
    def generate_single(self, password):
        """Genera MD5 de una sola palabra"""
        password = password.strip()
        if not password:
            return None
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    
    def get_results(self):
        """Devuelve los resultados generados"""
        return self.results