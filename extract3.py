import pdfplumber
import re
import os

# Ruta fija al PDF y al TXT de salida
PDF_PATH = r'D:\Kroger\Workspace\extraer_Texto\Nuevo.pdf'
OUTPUT_TXT = r'D:\Kroger\Workspace\extraer_Texto\output_Nuevo.txt'

# Opcional: número de bays y estantes por bay (para referencia)
NUM_BAYS = 3
SHELVES_PER_BAY = {1: 7, 2: 7, 3: 7}


def parse_pdf(pdf_path: str, output_txt: str):
    """
    Extrae información estructurada de un planograma en PDF y la guarda en un TXT.
    - Página 1: solo encabezados.
    - Páginas 2-3: secciones de productos NEW, DELETE, CHANGE.
    - Posteriores: detalle por Bay y Shelf.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"El archivo PDF '{pdf_path}' no existe.")

    with pdfplumber.open(pdf_path) as pdf, open(output_txt, 'w', encoding='utf-8') as out:
        total_pages = len(pdf.pages)

        # Página 1: encabezados
        lines0 = [ln.strip() for ln in (pdf.pages[0].extract_text() or '').splitlines() if ln.strip()]
        for ln in lines0:
            low = ln.lower()
            if low.startswith('nombre de plroyecto') or low.startswith('effective date') or low.startswith('period week'):
                out.write(ln + '\n')
        out.write(f"Page: 1 of {total_pages}\n\n")

        # Páginas 2 y 3: secciones de productos
        product_sections = ['NEW', 'DELETE', 'CHANGE']
        for idx in [1, 2]:
            if idx >= total_pages:
                break
            lines = [ln.strip() for ln in (pdf.pages[idx].extract_text() or '').splitlines() if ln.strip()]
            wrote_any = False
            for sect in product_sections:
                header_pattern = re.compile(rf"Products .*\({sect}\)", re.IGNORECASE)
                for i, ln in enumerate(lines):
                    if header_pattern.search(ln):
                        wrote_any = True
                        out.write(ln + '\n')
                        for itm in lines[i+1:]:
                            if any(re.search(rf"Products .*\({s}\)", itm, re.IGNORECASE) for s in product_sections):
                                break
                            out.write(itm + '\n')
                        out.write('\n')
                        break
            if wrote_any:
                out.write(f"Page: {idx+1} of {total_pages}\n\n")

        # Páginas posteriores: detalle Bay
        bay_header_re = re.compile(r"^Bay \d+.*")
        item_re = re.compile(r"^\d+\s+\d+\s+\d+\s+\d+")
        for idx in range(3, total_pages):
            lines = [ln.strip() for ln in (pdf.pages[idx].extract_text() or '').splitlines() if ln.strip()]
            i = 0
            while i < len(lines):
                ln = lines[i]
                if bay_header_re.match(ln):
                    out.write(ln + '\n')
                    if i+1 < len(lines) and lines[i+1].startswith('Bay Fi'):
                        out.write(lines[i+1] + '\n')
                        i += 2
                        while i < len(lines) and item_re.match(lines[i]):
                            out.write(lines[i] + '\n')
                            i += 1
                    out.write('\n')
                else:
                    i += 1
            out.write(f"Page: {idx+1} of {total_pages}\n\n")

    print(f"Generado: {output_txt}")


# Ejecución directa sin argumentos
def main():
    parse_pdf(PDF_PATH, OUTPUT_TXT)

if __name__ == '__main__':
    main()
