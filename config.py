# config.py

# ✅ Known form types with keyword matching
KNOWN_FORMS = {
    "Health Information Form": ["health information", "fairfax county public schools", "student health form"],
    "Enrollment Form": ["student enrollment", "admission", "registration"],
    "Medical History Form": ["medical history", "health conditions", "medications"]
}

# ✅ Static verbiage to remove (long repetitive instructions)
LONG_STATIC_VERBIAGE = [
    "Complete this form every school year to inform us about your student's",
    "Parental Consent: I agree to allow my child's healthcare provider(s) to discuss information",
    "Number of Emergency Room (ER) Visits in the last calendar year:",
    "existing and new health conditions that affect your student's school day"
]
