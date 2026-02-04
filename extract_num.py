#!/usr/bin/env python3
# extract_13digits.py

import re

def extract_13_digit_numbers(input_path, output_path, unique=True):
    """
    Extrae todas las secuencias de 13 dígitos de input_path y las guarda en output_path.
    
    Parámetros:
    - input_path: ruta del archivo de texto de entrada.
    - output_path: ruta del archivo de texto de salida.
    - unique: si True, elimina duplicados.
    """
    # Leer todo el contenido del archivo de entrada
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Buscar todas las secuencias de 13 dígitos
    matches = re.findall(r'\b\d{13}\b', text)
    
    # Si queremos sólo valores únicos
    if unique:
        matches = sorted(set(matches))
    
    # Escribir los resultados en el archivo de salida
    with open(output_path, 'w', encoding='utf-8') as f:
        for num in matches:
            f.write(num + '\n')

if __name__ == '__main__':
    # --- Ajusta aquí tus rutas de archivo: ---
    input_file  = 'D:\Kroger\Workspace\extraer_Texto\origen.txt'
    output_file = 'D:\Kroger\Workspace\extraer_Texto\salida.txt'
    # -----------------------------------------

    extract_13_digit_numbers(input_file, output_file)
    print(f"Proceso completado.\nSe han extraído los números de 13 dígitos de:\n  {input_file}\ny se han guardado en:\n  {output_file}")
