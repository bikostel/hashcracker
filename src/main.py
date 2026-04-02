# src/main.py
import tkinter as tk
from src.ui.app import HashCrackerGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = HashCrackerGUI(root)
    root.mainloop()