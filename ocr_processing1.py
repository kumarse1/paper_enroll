import pytesseract
from config import LONG_STATIC_VERBIAGE
import pandas as pd
from tabulate import tabulate
import re

def map_to_baseline_schema(word):
    """
    Map extracted text to a baseline schema based on patterns.
    This is a simple example - you should customize this function based on your specific needs.
    """
    # Example patterns - customize these for your document types
    patterns = {
        r'(?i)invoice\s*#?\s*:?\s*([A-Z0-9-]+)': 'Invoice Number',
        r'(?i)date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})': 'Date',
        r'(?i)total\s*:?\s*\$?(\d+\.\d{2})': 'Total Amount',
        r'(?i)customer\s*:?\s*([A-Za-z0-9\s]+)': 'Customer',
        # Add more patterns as needed
    }
    
    mapped_field = "Unknown"
    for pattern, field_name in patterns.items():
        if re.search(pattern, word):
            mapped_field = field_name
            break
            
    return mapped_field

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
                    complete_word = " ".join(word_buffer)
                    mapped_schema = map_to_baseline_schema(complete_word)
                    extracted_text.append({
                        "key": complete_word.split(':')[0].strip() if ':' in complete_word else complete_word,
                        "value": complete_word.split(':')[1].strip() if ':' in complete_word else "",
                        "confidence": confidence,
                        "mapped_schema": mapped_schema,
                        "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h}
                    })
                word_buffer = [word]
            prev_x = x + w
    if word_buffer:
        complete_word = " ".join(word_buffer)
        mapped_schema = map_to_baseline_schema(complete_word)
        extracted_text.append({
            "key": complete_word.split(':')[0].strip() if ':' in complete_word else complete_word,
            "value": complete_word.split(':')[1].strip() if ':' in complete_word else "",
            "confidence": confidence,
            "mapped_schema": mapped_schema,
            "bounding_box": {"x": prev_x, "y": y, "width": w, "height": h}
        })
    return extracted_text

def print_ocr_results_table(extracted_text):
    """Print OCR results in a nicely formatted table"""
    # Create a pandas DataFrame from the extracted text
    df = pd.DataFrame([{
        'Key': item['key'],
        'Value': item['value'],
        'Confidence': f"{item['confidence']}%",
        'Mapped Schema': item['mapped_schema']
    } for item in extracted_text])
    
    # Print using tabulate for a nice table format
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
    # Return the dataframe in case you want to use it for other purposes
    return df

# Example usage
if __name__ == "__main__":
    from PIL import Image
    
    # Replace with your image path
    image_path = "your_document.png"
    image = Image.open(image_path)
    
    # Perform OCR
    results = perform_ocr(image)
    
    # Print results in tabular format
    print_ocr_results_table(results)
