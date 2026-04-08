# 🔐 Hash Cracker — Offline

Una aplicación Windows de escritorio para crackear hashes MD5 offline usando dos métodos:
- **Diccionario**: Comparación rápida contra un wordlist
- **Fuerza Bruta**: Generación y prueba de combinaciones de caracteres

## ✨ Características

- ✅ **100% Offline** — Sin conexión a internet
- ✅ **GUI Simple** — Interfaz gráfica intuitiva para Windows
- ✅ **Dos métodos de cracking**:
  - Diccionario (rápido)
  - Fuerza bruta (exhaustivo)
- ✅ **Multi-threading** — Procesamiento paralelo para mayor velocidad
- ✅ **Bajo consumo** — Optimizado para máquinas antiguas
- ✅ **Portable** — Un único .exe, sin dependencias externas
- ✅ **Exportación CSV** — Guarda resultados en archivo

---

## 📋 Requisitos

### Opción 1: Ejecutable (.exe)
- Windows 7, 8, 10, 11 (XP+ con Python 3.8+)
- Sin necesidad de instalar nada

### Opción 2: Ejecutar desde código fuente
- **Python 3.8+** (https://www.python.org/downloads/)
- **Sin dependencias externas** (solo librerías estándar: `hashlib`, `threading`, `tkinter`)

---

## 🚀 Instalación y Uso

### Opción A: Descargar el .exe (más fácil)

1. Ve a **Releases** → descarga `HashCracker.exe`
2. Ejecuta el archivo
3. ¡Listo! No necesitas Python

### Opción B: Clonar el repositorio

```bash
git clone https://github.com/bikostel/hashcracker.git
cd hashcracker
python src/main.py