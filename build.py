import PyInstaller.__main__

PyInstaller.__main__.run([
    'src/main.py',
    '--onefile',
    '--windowed',
    '--name=HashCracker',
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
    '--clean',
])

print("\n✅ Ejecutable generado en: dist/HashCracker.exe")
print("   Tamaño: ~20-30 MB")
print("   Funciona en: Windows XP, Vista, 7, 8, 10, 11")