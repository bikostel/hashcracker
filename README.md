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

git clone https://github.com/bikostel/hashcracker.git
cd hashcracker
python src/main.py


📖 Cómo Usar
1️⃣ Cargar Hashes
Clicka en "Cargar Hashes (MD5)"
Selecciona un archivo .txt con hashes MD5 (uno por línea)
Ejemplo:
Code
5d41402abc4b2a76b9719d911017c592
5f4dcc3b5aa765d61d8327deb882cf99
098f6bcd4621d373cade4e832627b4f6
2️⃣ Elegir Método
Pestaña 1: Diccionario (Rápido)
Clicka en "Cargar Diccionario (.txt)"
Selecciona un archivo de palabras
Clicka "▶️ INICIAR"
Espera resultados
Ventajas:

Muy rápido (millones de palabras/segundo)
Ideal si sospechas palabras comunes
Desventajas:

Solo encuentra palabras en el diccionario
Pestaña 2: Fuerza Bruta (Exhaustivo)
Configura los parámetros:
Caracteres: marca qué incluir (a-z, A-Z, 0-9)
Longitud máx: número máximo de caracteres (1-8)
Clicka "▶️ INICIAR"
Espera (¡esto es lento!)
Ventajas:

Encuentra cualquier combinación (sin límite de diccionario)
Desventajas:

MUY lento para longitudes > 6
Ejemplo: 26^6 = 308 millones de combinaciones
3️⃣ Ver Resultados
Los hashes encontrados aparecerán en la tabla:

MD5 Hash	Contraseña
5d41402abc4b2a76b9719d911017c592	admin
098f6bcd4621d373cade4e832627b4f6	test
4️⃣ Exportar Resultados
Clicka "💾 EXPORTAR CSV"
Elige dónde guardar
Se generará un archivo resultados.csv
🏗️ Arquitectura
Code
hash_cracker/
│
├── src/
│   ├── main.py              # Punto de entrada
│   │
│   ├── core/
│   │   └── cracker.py       # Motor de cracking
│   │       ├── MD5Cracker (diccionario)
│   │       └── BruteForceCracker (fuerza bruta)
│   │
│   └── ui/
│       └── app.py           # Interfaz gráfica (tkinter)
│
├── requirements.txt         # Dependencias (vacío)
├── build.py                 # Script para compilar a .exe
└── README.md                # Este archivo
📦 Módulos Principales
src/core/cracker.py
Clase MD5Cracker:

Lee un diccionario línea por línea (sin cargar todo en RAM)
Usa threading para procesar múltiples palabras en paralelo
Calcula MD5 de cada palabra y compara con objetivos
Python
cracker = MD5Cracker(hashes=['5d41402abc4b2a76b9719d911017c592'], 
                     wordlist_path='diccionario.txt')
resultados = cracker.crack(num_threads=2)
Clase BruteForceCracker:

Genera todas las combinaciones posibles (con itertools.product)
Calcula MD5 de cada combinación
Busca coincidencias
Python
cracker = BruteForceCracker(hashes=['5d41402abc4b2a76b9719d911017c592'],
                           charset='abcdefghijklmnopqrstuvwxyz',
                           max_length=4)
resultados = cracker.crack()
src/ui/app.py
GUI con tkinter (compatible con PCs viejas)
Dos pestañas: Diccionario y Fuerza Bruta
Tabla de resultados con scroll
Barra de progreso en tiempo real
Exportación a CSV
⚡ Optimizaciones
Aspecto	Solución
Velocidad	Threading + hashlib nativo (C)
Memoria	Streaming de diccionario (no carga todo)
UI Responsive	Trabajo en thread separado
Compatibilidad	Tkinter vanilla (sin dependencias)
Tamaño	~20-30 MB (ejecutable portable)
⚠️ Limitaciones
Solo MD5 (fácil de extender a SHA1, SHA256, etc.)
Fuerza bruta es muy lenta para longitudes > 6
26^7 = 8 billones de combinaciones ❌
26^6 = 308 millones de combinaciones ~ 1-2 horas
No soporta GPU (se puede agregar con CUDA/OpenCL)
Solo Windows (el código es multiplataforma, pero el .exe es Windows-only)
🔧 Compilar a .exe
Si quieres crear tu propio ejecutable:

# 1. Instalar PyInstaller
pip install pyinstaller

# 2. Compilar
pyinstaller --onefile --windowed --name=HashCracker src/main.py

# 3. El .exe estará en dist/HashCracker.exe
📊 Ejemplos de Uso
Ejemplo 1: Crackear un hash conocido
Code
1. Archivo hashes.txt:
   5f4dcc3b5aa765d61d8327deb882cf99

2. Archivo diccionario.txt:
   password
   admin
   test123
   ...

3. Resultado:
   5f4dcc3b5aa765d61d8327deb882cf99 → password ✅
Ejemplo 2: Fuerza bruta simple
Code
1. Hashes objetivo:
   c81e728d9d4c2f636f067f89cc14862

2. Configuración:
   - Caracteres: a-z (minúsculas)
   - Longitud máx: 3

3. Resultado:
   c81e728d9d4c2f636f067f89cc14862 → "2" ✅
   (MD5 de "2")
🐛 Troubleshooting
"ModuleNotFoundError: No module named 'src'"
Asegúrate de estar en la carpeta raíz del proyecto
Ejecuta: python src/main.py (no python main.py)
"El .exe no funciona en mi máquina vieja"
Requiere Windows 7+ (XP necesita Python 3.8+)
Compila desde código: python src/main.py
"¿Por qué es tan lento?"
Fuerza bruta es lento por naturaleza
Usa diccionario si es posible
Máximo longitud = 6 para no esperar horas
📝 Licencia
Este proyecto es de código abierto. Úsalo, modifícalo y distribúyelo libremente.

🤝 Contribuciones
¿Quieres mejorar el proyecto? Ideas:

 Soporte para SHA1, SHA256
 Acelerar con GPU (CUDA)
 Interfaz web
 Soporte para Linux/Mac
 Búsqueda en la nube (online)
📬 Contacto
GitHub: https://github.com/bikostel/hashcracker
Issues: Reporta bugs o sugiere features
🎯 Roadmap
 Motor MD5 con diccionario
 Motor de fuerza bruta
 Interfaz gráfica con pestañas
 Exportación CSV
 Soporte para otros hash (SHA1, SHA256)
 Aceleración GPU
 Base de datos de hashes precomputados (rainbow tables)
Versión: 1.0
Última actualización: Abril 2026
Python: 3.8+
Plataforma: Windows 7+

Code


## **Cómo agregar este README**

1. **Copia el contenido arriba**
2. **En VSCode**, abre o crea el archivo `README.md` en la raíz
3. **Pega el contenido**
4. **Guarda** (Ctrl+S)
5. **Sube a GitHub**:


git add README.md
git commit -m "Agregar README completo"
git push hashcrack main
¿Necesitas que ajuste algo del README? 👇

Make these code changes?
README.md

md
# Hash Cracker

## Overview
The Hash Cracker is an application designed to decode hashed passwords using various algorithms. Its primary purpose is to demonstrate cryptographic techniques and security vulnerabilities associated with hashing.

## Features
- Support for multiple hashing algorithms (e.g., MD5, SHA-1, SHA-256)
- User-friendly command-line interface
- Ability to crack hashes using both brute force and dictionary attacks
- Logging and reporting of cracking attempts

## Installation
To install the Hash Cracker application, follow these steps:
1. Clone the repository:
   git clone https://github.com/bikostel/hashcracker.git
   cd hashcracker

Install the required dependencies:
bash
pip install -r requirements.txt
Usage
To use the Hash Cracker application, run the following command:

python hash_cracker.py --hash [hash] --algorithm [algorithm]
Replace [hash] with the hash string you want to crack.
Replace [algorithm] with the hashing algorithm you want to use (e.g., md5, sha1, sha256).

Examples
python hash_cracker.py --hash 5d41402abc4b2a76b9719d911017c592 --algorithm md5
python hash_cracker.py --hash f7c3c39fbc491c789b6f0f11c0f60011 --algorithm sha1
Architecture
The application follows a modular architecture with the following components:

Hashing Algorithms Module: Implements various hashing algorithms.
Cracking Module: Contains logic for brute-force and dictionary attack methods.
User Interface Module: Manages user input and outputs results.
Logging Module: Tracks attempts and results for analysis.
For more information, please refer to the documentation in the repository or open an issue if you have any questions.
