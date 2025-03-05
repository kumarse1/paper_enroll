import streamlit as st
import pandas as pd
import json
from text_analysis import validate_extracted_data, load_baseline_schema

# ✅ Load baseline schema
baseline_schema = load_baseline_schema()

# ✅ Streamlit UI: Add a New Tab for Validation Results
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📄 Uploaded Document", "🖼️ Cleaned Image", "🔍 Extracted Fields (Table)", "📊 Confidence Scores", "📝 Full JSON Output", "✅ Validation Results"]
)

with tab6:
    st.subheader("✅ Validation Against Expected Format")
    
    # Simulated Extracted Data for Testing
    extracted_data = {
        "First Name": "John",
        "Last Name": "Doe",
        "SSN": "123-45-678",
        "Date of Birth": "06/15/1985"
    }

    validation_results = validate_extracted_data(extracted_data, baseline_schema)

    # ✅ Convert results into a DataFrame
    validation_df = pd.DataFrame.from_dict(validation_results, orient="index")

    # ✅ Apply conditional formatting for color coding results
    def color_valid(val):
        if val == True:
            return "background-color: #c8e6c9; color: #1b5e20;"  # Green ✅
        elif val == False:
            return "background-color: #ffcdd2; color: #b71c1c;"  # Red ❌
        return ""

    # ✅ Show the results in a color-coded table
    st.dataframe(validation_df.style.applymap(color_valid, subset=["valid"]))
