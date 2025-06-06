import streamlit as st
import pytesseract
from pytesseract import Output
from PIL import Image
import cv2
import numpy as np
import json
import hashlib
import requests

st.title("🧾 Form Schema Extractor (PyTesseract + Vision LLM API)")

# --- Configurable API settings ---
vision_llm_api_url = st.text_input("🔧 Vision LLM API Endpoint", "http://localhost:8000/api/vision")
vision_llm_auth_token = st.text_input("🔐 Optional Bearer Token (if needed)", type="password")

uploaded_file = st.file_uploader("📤 Upload a blank form image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    # --- Step 1: Preprocess Image ---
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # --- Step 2: Generate Unique ID for the Form ---
    form_bytes = image.tobytes()
    form_hash = hashlib.md5(form_bytes).hexdigest()
    st.success(f"📄 Unique Form ID (MD5): {form_hash}")

    # --- Step 3: OCR with bounding boxes and context ---
    ocr_data = pytesseract.image_to_data(thresh, output_type=Output.DICT)
    n_boxes = len(ocr_data['text'])

    results = []
    for i in range(n_boxes):
        if int(ocr_data['conf'][i]) > 60:
            text = ocr_data['text'][i].strip()
            if text:
                x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                results.append({
                    "text": text,
                    "bbox": [x, y, x + w, y + h],
                    "confidence": int(ocr_data['conf'][i]),
                    "line_num": ocr_data['line_num'][i],
                    "block_num": ocr_data['block_num'][i],
                    "page_num": ocr_data['page_num'][i],
                    "width": w,
                    "height": h
                })
                cv2.rectangle(img_np, (x, y), (x + w, y + h), (0, 255, 0), 2)

    st.image(img_np, caption="Detected text with bounding boxes", channels="RGB")

    # --- Step 4: Generate prompt for Vision LLM ---
    if results:
        st.subheader("🔍 OCR Output")
        st.json(results)

        form_meta = {
            "form_id": form_hash,
            "image_width": image.width,
            "image_height": image.height,
            "num_ocr_entries": len(results)
        }

        prompt = f"""
You are a Vision LLM helping extract structured form schema from OCR data.

OCR data was extracted from a blank form template using PyTesseract. Your goal is to:
✅ Identify fields that a human would be expected to fill in
✅ Provide the field name (as labeled on the form)
✅ Determine the data type (string, number, date, etc.)
✅ Return the exact bounding box that represents the user-input area — not the label
✅ If possible, assign a logical section name (e.g., 'Member Info', 'Dependent Info', 'Signature') based on headings, titles, or spatial grouping

You are also given line numbers, block numbers, and page numbers. Use these to group related fields into logical sections or detect if the form spans multiple pages.

❌ Do NOT return bounding boxes for labels only (e.g., 'Patient Name')
❌ Do NOT include decorative text or titles
❌ Do NOT guess values — only infer where the input is expected
❌ Exclude paragraphs or blocks of legal disclaimers, instructions, or small-font text commonly found in footers or margins

Form Metadata:
{json.dumps(form_meta, indent=2)}

Input OCR JSON:
{json.dumps(results, indent=2)}

Return your output as a JSON array of objects with these fields:
- field_name
- data_type
- bounding_box
- section_name (optional but recommended if identifiable)
"""

        st.subheader("🧠 Prompt for Vision LLM")
        st.code(prompt, language="text")

        # --- Step 5: Send to Vision LLM API ---
        if st.button("🚀 Call Vision LLM API"):
            files = {"image": uploaded_file.getvalue()}
            data = {"prompt": prompt}
            headers = {"Authorization": f"Bearer {vision_llm_auth_token}"} if vision_llm_auth_token else {}

            with st.spinner("Calling Vision LLM..."):
                try:
                    response = requests.post(vision_llm_api_url, files=files, data=data, headers=headers)
                    response.raise_for_status()
                    st.subheader("📦 Vision LLM Response")
                    st.json(response.json())
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Vision LLM API call failed: {e}")
    else:
        st.warning("⚠️ No high-confidence text detected. Try a clearer image or different form.")

 
