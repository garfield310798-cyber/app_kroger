import cv2
from PIL import Image
import pytesseract
import pandas as pd
import os

IMG_PATH = r'D:\Kroger\Workspace\extraer_Texto\SCN_20250728_101914.jpg'
OUT_CSV  = r'D:\Kroger\Workspace\extraer_Texto\texto_local.csv'

print("CWD:", os.getcwd())
print("Existe la imagen?", os.path.exists(IMG_PATH))


# 1) Carga y convierte a gris
img_cv = cv2.imread(IMG_PATH)
gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

# 2) Detecta bloques
def detect_blocks(gray):
    _, bw = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50,20))
    closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blocks = []
    for cnt in contours:
        x,y,w,h = cv2.boundingRect(cnt)
        if w*h < 5000: continue
        blocks.append((x,y,w,h))
    return sorted(blocks, key=lambda b: (b[1], b[0]))

blocks = detect_blocks(gray)

# 3) OCR por bloque
results = []
img_pil = Image.open(IMG_PATH)
for i, (x,y,w,h) in enumerate(blocks, 1):
    roi = img_pil.crop((x, y, x+w, y+h))
    text = pytesseract.image_to_string(roi, config='--psm 6').strip()
    if text:
        results.append({
            'block_id': i,
            'left': x, 'top': y,
            'width': w, 'height': h,
            'text': text.replace('\n',' ')
        })

# 4) Guardar CSV sólo con texto, un bloque por fila
df = pd.DataFrame(results)

# Opción A: con cabecera “text”
df[['text']].to_csv(OUT_CSV, index=False, header=True, encoding='utf-8')

# Opción B: sin cabecera (justo el texto plano)
# df['text'].to_csv(OUT_CSV, index=False, header=False, encoding='utf-8')

print(f"Extracción completa: {len(df)} bloques anotados. CSV: {OUT_CSV}")

