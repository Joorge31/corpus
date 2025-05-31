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
        
librerias_necesarias=["os", "re","pandas", "string", "langdetect", "tkinter", "pymupdf", "pytesseract", "PIL", "io","difflib", "Levenshtein", "configparser"]
for libreria in librerias_necesarias:
    instala_importa(libreria)
	
import pymupdf
import pytesseract
from PIL import Image
import io
import difflib
import Levenshtein
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import configparser
config=configparser.ConfigParser()
config.read("config.ini")
RUTA_TESERACT=config.get('settings','RUTA_TESERACT')
pytesseract.pytesseract.tesseract_cmd = RUTA_TESERACT

# Abre ventana para seleccionar el PDF
def seleccionar_pdf():
    root = tk.Tk()
    root.withdraw()
    pdf_path = filedialog.askopenfilename(
        title="Selecciona el folleto PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    root.destroy()
    return pdf_path

pdf_path = seleccionar_pdf()
if not pdf_path:
    print("No se seleccionó ningún archivo.")
    exit()

# Extrae el nombre base del archivo (sin extensión, ni carpeta)
nombre_base = os.path.splitext(os.path.basename(pdf_path))[0]

# Construye el nombre del CSV
csv_name = f"analisis_{nombre_base}.csv"

doc = pymupdf.open(pdf_path)
resultados = []




data = []

for i in range(doc.page_count):
    # Extraer texto con PyMuPDF
    pagina = doc.load_page(i)
    texto_pymupdf = pagina.get_text().strip()
    
    # Extraer texto con pytesseract (OCR)
    pix = pagina.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    texto_ocr = pytesseract.image_to_string(img, lang='spa').strip()
    
    # --- Métricas a nivel de carácter ---
    n_caracteres_ref = len(texto_pymupdf)
    n_caracteres_ocr = len(texto_ocr)
    ops = Levenshtein.editops(texto_pymupdf, texto_ocr)
    inserciones = sum(1 for op in ops if op[0] == 'insert')
    eliminaciones = sum(1 for op in ops if op[0] == 'delete')
    sustituciones = sum(1 for op in ops if op[0] == 'replace')
    correctos = n_caracteres_ref - eliminaciones - sustituciones
    
    # --- Métricas a nivel de palabra ---
    palabras_ref = texto_pymupdf.split()
    palabras_ocr = texto_ocr.split()
    n_palabras_ref = len(palabras_ref)
    n_palabras_ocr = len(palabras_ocr)
    palabras_correctas = sum(1 for a, b in zip(palabras_ref, palabras_ocr) if a == b)
    print(f'analizando la página {i+1}')
    data.append({
        'pagina': i + 1,
        'n_caracteres_ref': n_caracteres_ref,
        'n_caracteres_ocr': n_caracteres_ocr,
        'correctos': correctos,
        'inserciones': inserciones,
        'eliminaciones': eliminaciones,
        'sustituciones': sustituciones,
        'n_palabras_ref': n_palabras_ref,
        'n_palabras_ocr': n_palabras_ocr,
        'palabras_correctas': palabras_correctas,
        'texto_ref': texto_pymupdf,
        'texto_ocr': texto_ocr
    })

# Guardar todas las métricas en un CSV
df = pd.DataFrame(data)
df.to_csv(csv_name, index=False)
print(df.head())