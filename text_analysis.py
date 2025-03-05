import json
import re

# ✅ Load Baseline Schema for Validation
def load_baseline_schema(schema_path="baseline_schema.json"):
    """Loads expected field schema from JSON file."""
    with open(schema_path, "r") as f:
        return json.load(f)

# ✅ Detect Form Type Based on Keywords
def detect_form_type(ocr_text):
    """Detects form type based on extracted text."""
    KNOWN_FORMS = {
        "Health Information Form": ["health information", "fairfax county public schools", "student health form"],
        "Enrollment Form": ["student enrollment", "admission", "registration"],
        "Medical History Form": ["medical history", "health conditions", "medications"]
    }

    for form_name, keywords in KNOWN_FORMS.items():
        for keyword in keywords:
            if keyword.lower() in ocr_text.lower():
                return form_name
    return "Unknown Form"

# ✅ Structure JSON Output
def structure_to_json(ocr_results, form_type):
    """Structures extracted OCR results into JSON."""
    return {"form_type": form_type, "real_values": ocr_results}

# ✅ Validate Extracted Data Against Expected Format
def validate_extracted_data(extracted_data, baseline_schema):
    """Compares OCR-extracted data against expected format."""
    validation_results = {}

    for field, rules in baseline_schema["expected_fields"].items():
        extracted_value = extracted_data.get(field, "")

        # ✅ Ensure extracted_value is always a string
        extracted_value = str(extracted_value) if extracted_value is not None else ""

        pattern = rules["pattern"]
        is_valid = bool(re.match(pattern, extracted_value)) if extracted_value else False

        validation_results[field] = {
            "valid": is_valid,
            "expected_format": pattern,
            "extracted_value": extracted_value if is_valid else "MISSING/INVALID"
        }
    
    return validation_results