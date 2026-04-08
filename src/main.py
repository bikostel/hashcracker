# src/main.py
import sys
import os

# Añade la carpeta raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from src.ui.app import HashCrackerGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = HashCrackerGUI(root)
    root.mainloop()