# pdf_processing.py
import fitz  # PyMuPDF
from PIL import Image

def pdf_to_images(pdf_path):
    """Extracts images from a PDF file using PyMuPDF (fitz)."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images
