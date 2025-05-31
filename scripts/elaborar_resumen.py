import sys
import subprocess

#comprueba si están instaladas y, si no, las instala
def instala_importa(libreria):
    try:
        __import__(libreria)
    except ImportError:
        print(f"Instalando {libreria}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", libreria])
        print(f"{libreria} instalado exitosamente.")
        
librerias_necesarias=["os", "re","pandas", "string", "langdetect", "tkinter"]
for libreria in librerias_necesarias:
    instala_importa(libreria)



import os
import re
import pandas as pd
import string
from langdetect import detect, LangDetectException
import tkinter as tk
from tkinter import filedialog

def pedir_directorio():
    root = tk.Tk()
    root.withdraw()
    directorio = filedialog.askdirectory(title="Selecciona el directorio raíz de los resultados")
    root.destroy()
    return directorio

directorio_raiz = pedir_directorio()

umbral_palabras_legible = 10  

def es_legible(texto, umbral_palabras=umbral_palabras_legible, umbral_printables=0.85):
    palabras = re.findall(r'\b\w+\b', texto)
    n_palabras = len(palabras)
    propor_printables = sum(c in string.printable for c in texto) / max(1, len(texto))
    return (n_palabras >= umbral_palabras) and (propor_printables >= umbral_printables)



def detectar_idioma(texto):
    try:
        lang = detect(texto)
        if lang == 'es':
            return 'castellano'
        elif lang == 'en':
            return 'inglés'
        else:
            return lang
    except LangDetectException:
        return 'desconocido'

datos = []

for root, dirs, files in os.walk(directorio_raiz):
    for nombre_archivo in files:
        if nombre_archivo.startswith('No_OCR') and nombre_archivo.endswith('completo.txt'):
            ruta_archivo = os.path.join(root, nombre_archivo)
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                texto = f.read()
                palabras = re.findall(r'\b\w+\b', texto)
                n_palabras = len(palabras)
                legible = es_legible(texto)
                idioma = detectar_idioma(texto)
                datos.append({
                    'ruta': ruta_archivo,
                    'n_palabras': n_palabras,
                    'legible': legible,
                    'idioma': idioma
                })

df = pd.DataFrame(datos)
print(df)
df.to_csv('resumen_No_OCR_completo.csv', index=False)