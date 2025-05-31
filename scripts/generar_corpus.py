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
        
librerias_necesarias=["os", "re","pandas", "string", "langdetect", "tkinter", "pymupdf", "pytesseract", "PIL","fitz", "io","difflib", "Levenshtein", "configparser", "pdfplumber"]
for libreria in librerias_necesarias:
    instala_importa(libreria)
	
import pymupdf
import pytesseract
from PIL import Image
import io
import difflib
import Levenshtein
import os
import re
import fitz
import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import configparser
config=configparser.ConfigParser()
config.read("config.ini")
RUTA_TESERACT=config.get('settings','RUTA_TESERACT')
pytesseract.pytesseract.tesseract_cmd = RUTA_TESERACT



pytesseract.pytesseract.tesseract_cmd = RUTA_TESERACT
IDIOMA_OCR = 'spa'  
UMBRAL_LEGIBILIDAD = 0.6  



def seleccionar_pdf(title):
    root = tk.Tk()
    root.withdraw()
    directorio = filedialog.askdirectory(title=title)
    root.destroy()
    return directorio



def aplicar_ocr_a_imagen(imagen, lang=IDIOMA_OCR):
    try:
        return pytesseract.image_to_string(imagen, lang=lang)
    except pytesseract.TesseractNotFoundError:
        raise Exception("Tesseract no instalado. Descárgalo desde https://github.com/UB-Mannheim/tesseract/wiki")


# Procesador de PDFs

def procesar_pdf(pdf_path, output_dir, extraer_tablas=True, extraer_imagenes=True):
    # Crear directorios de salida
    base_name = limpiar_nombre(os.path.splitext(os.path.basename(pdf_path))[0])    
    main_dir = os.path.join(output_dir, base_name)
    txt_dir = main_dir
    img_dir = os.path.join(main_dir, "imagenes")
    tablas_dir = os.path.join(main_dir, "tablas")
    print(base_name)
    print(main_dir)
    print(txt_dir)
    print(img_dir)
    print(tablas_dir)
     
    os.makedirs(txt_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(tablas_dir, exist_ok=True)
    
    # Inicializar informe
    informe = {
        'total_paginas': 0,
        'texto_nativo':'',
        'texto_extraido': '',
        'tablas_extraidas': 0
    }
    
    # Procesar PDF
    with fitz.open(pdf_path) as doc, pdfplumber.open(pdf_path) as pdf_plumber:
        informe['total_paginas'] = len(doc)
        necesita_ocr = False
        for page_num in range(len(doc)):
            texto_pagina = ''
            
            
            # Intentar extracción de texto nativo
            pagina_pymupdf = doc.load_page(page_num)
            texto_nativo = pagina_pymupdf.get_text()
            

            # Convertir página a imagen y aplicar OCR
            pix = pagina_pymupdf.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pdf_file = "folletos/folleto_imbcccapital1.pdf"
            texto_pagina += pytesseract.image_to_string(img, lang="spa")  # Cambia 'spa' por el idioma adecuado

            
            informe['texto_extraido'] += texto_pagina + "\f"
            informe['texto_nativo']+= texto_nativo + "\f"

            if extraer_tablas: 
                pagina_plumber = pdf_plumber.pages[page_num]
                tablas = pagina_plumber.extract_tables()
                
                for i, tabla in enumerate(tablas):
                    nombre_tabla = f"pagina_{page_num+1}_tabla_{i+1}.csv"
                    ruta_tabla = os.path.join(tablas_dir, nombre_tabla)
                    
                    with open(ruta_tabla, 'w', encoding='utf-8') as f:
                        for fila in tabla:
                            f.write(','.join(str(celda) if celda else '' for celda in fila) + '\n')
                    informe['tablas_extraidas'] += 1
            
            # Extraer imágenes
            if extraer_imagenes:
                imagenes = pagina_pymupdf.get_images()
                for img_index, img in enumerate(imagenes):
                    base_image = doc.extract_image(img[0])
                    extension = base_image['ext']
                    nombre_imagen = f"pagina_{page_num+1}_imagen_{img_index+1}.{extension}"
                    with open(os.path.join(img_dir, nombre_imagen), "wb") as f:
                        f.write(base_image["image"])
    
    # Guardar texto completo
    with open(os.path.join(txt_dir, f"{base_name}_completo.txt"), 'w', encoding='utf-8') as f:
        f.write(informe['texto_extraido'])
    with open(os.path.join(txt_dir, f"NO_OCR_{base_name}_completo.txt"), 'w', encoding='utf-8') as f:
        f.write(informe['texto_nativo'])
    
    return informe

def limpiar_nombre(nombre):
    return re.sub(r'[<>:"/\\|?*]', '_', nombre).strip()

# Ejecución principal
resultados = []

    

directorio_entrada = seleccionar_pdf("Selecciona el directorio donde están los pdf")
directorio_salida = seleccionar_pdf("Selecciona el directorio donde quieres que se guarden las extracciones")

for nombre_fichero in os.listdir(directorio_entrada):
	if nombre_fichero.lower().endswith(".pdf"):
		pdf_path = os.path.join(directorio_entrada, nombre_fichero)
		print(f"Procesando: {pdf_path}")
		informe = procesar_pdf(pdf_path, directorio_salida)
		

		resultados.append(informe)
resumen = pd.DataFrame(resultados)
resumen.to_excel("resumen_conversión.xlsx", index=False)