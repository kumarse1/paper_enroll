# ocr_processing.py
import pytesseract
from config import LONG_STATIC_VERBIAGE

def perform_ocr(image):
    """Extracts text with confidence, merges words, and filters static verbiage."""
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    extracted_text = []
    word_buffer = []
    prev_x = None

    for i in range(len(ocr_data["text"])):
        word = ocr_data["text"][i].strip()
        confidence = int(ocr_data["conf"][i])
        x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]

        if word and confidence > 50 and word not in LONG_STATIC_VERBIAGE:
            if prev_x is not None and (x - prev_x) < 15:
                word_buffer.append(word)
            else:
                if word_buffer:
                    extracted_text.append({"word": " ".join(word_buffer), "confidence": confidence,
                                           "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h}})
                word_buffer = [word]
            prev_x = x + w

    if word_buffer:
        extracted_text.append({"word": " ".join(word_buffer), "confidence": confidence,
                               "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h}})
    return extracted_text
