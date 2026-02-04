from PIL import Image
import pytesseract
import pandas as pd
import os

# 1) Ruta de la imagen
IMG_PATH = r'D:\Kroger\Workspace\extraer_Texto\SCN_20250728_101914.jpg'

# 2) Abrir y hacer OCR de todo el texto
img = Image.open(IMG_PATH)
raw_text = pytesseract.image_to_string(img, config='--psm 6')

# 3) Partir en líneas y limpiar vacíos
lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

# 4) Crear DataFrame y volcar a CSV
df = pd.DataFrame(lines, columns=['text'])
out_csv = os.path.splitext(IMG_PATH)[0] + '_lineas.csv'
df.to_csv(out_csv, index=False, encoding='utf-8')

print(f"Se generó {out_csv} con {len(lines)} líneas de texto.")
