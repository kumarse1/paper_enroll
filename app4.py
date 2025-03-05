import streamlit as st
import os
import json
import tempfile
import pandas as pd
from pdf_processing import pdf_to_images
from image_processing import preprocess_image, save_cleaned_image
from ocr_processing import perform_ocr
from text_analysis import detect_form_type, structure_to_json, validate_extracted_data, load_baseline_schema

# ✅ Load baseline schema
baseline_schema = load_baseline_schema()

# ✅ Set page title
st.set_page_config(page_title="📄 OCR Document Processor", layout="wide")

# ✅ Define max file size (3MB)
MAX_FILE_SIZE_MB = 3 * 1024 * 1024  # 3MB in bytes

st.title("📄 OCR Document Processing App")

# ✅ File Upload Section
uploaded_file = st.file_uploader("Drag and drop a PDF file (Max: 3MB)", type=["pdf"])

if uploaded_file:
    # ✅ Check file size
    if uploaded_file.size > MAX_FILE_SIZE_MB:
        st.error("🚨 File size exceeds 3MB! Please upload a smaller file.")
    else:
        st.success("✅ File uploaded successfully! Click **Submit** to process.")
        
        if st.button("🚀 Submit & Process"):
            with st.spinner("⏳ Processing document..."):
                # ✅ Save uploaded file temporarily
                temp_dir = tempfile.mkdtemp()
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)

                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # ✅ Process PDF
                images = pdf_to_images(temp_file_path)
                all_results = []
                cleaned_image_paths = []

                for i, image in enumerate(images):
                    processed_image = preprocess_image(image)
                    cleaned_image_path = os.path.join(temp_dir, f"cleaned_page_{i+1}.png")
                    save_cleaned_image(processed_image, temp_dir, i + 1)

                    ocr_results = perform_ocr(processed_image)
                    form_type = detect_form_type("\n".join([word["word"] for word in ocr_results]))
                    structured_json = structure_to_json(ocr_results, form_type)

                    structured_json["form_type"] = form_type  # Add detected form type
                    all_results.append(structured_json)
                    cleaned_image_paths.append(cleaned_image_path)

                # ✅ Save processed OCR output as JSON
                output_json_path = os.path.join(temp_dir, "filtered_ocr_output.json")
                with open(output_json_path, "w", encoding="utf-8") as json_file:
                    json.dump(all_results, json_file, indent=4)

                st.success("✅ OCR Processing Completed!")

                # ✅ UI - Display Results
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
                    ["📄 Uploaded Document", "🖼️ Cleaned Image", "🔍 Extracted Fields (Table)", "📊 Confidence Scores", "📝 Full JSON Output", "✅ Validation Results"]
                )

                with tab1:
                    st.subheader("Uploaded Document")
                    st.write(f"📂 File: `{uploaded_file.name}`")
                    st.download_button("📥 Download Original PDF", temp_file_path, file_name=uploaded_file.name)

                with tab2:
                    st.subheader("Cleaned OCR Image")
                    for img_path in cleaned_image_paths:
                        st.image(img_path, caption="Processed Image (Noise Removed)", use_column_width=True)
                        st.download_button("📥 Download Cleaned Image", img_path, file_name=os.path.basename(img_path))

                with tab3:
                    st.subheader("Extracted Fields (Table Format)")
                    extracted_text_data = []
                    for page in all_results:
                        for word in page["real_values"]:
                            extracted_text_data.append({
                                "Key": word["word"],  
                                "Confidence (%)": word["confidence"]
                            })
                    
                    if extracted_text_data:
                        df = pd.DataFrame(extracted_text_data)
                        st.dataframe(df)  # Display extracted data as a table
                    else:
                        st.warning("⚠️ No extracted fields found.")

                with tab4:
                    st.subheader("Confidence Scores Summary")
                    if extracted_text_data:
                        confidence_df = pd.DataFrame(extracted_text_data)
                        st.bar_chart(confidence_df.set_index("Key"))  # Show confidence scores as a bar chart
                    else:
                        st.warning("⚠️ No confidence scores found.")

                with tab5:
                    st.subheader("Full Extracted Data (JSON Format)")
                    st.json(all_results)

                with tab6:
                    st.subheader("✅ Validation Against Expected Format")

                    extracted_data = {
                        "First Name": "John",
                        "Last Name": "Doe",
                        "SSN": "123-45-678",
                        "Date of Birth": "06/15/1985"
                    }

                    validation_results = validate_extracted_data(extracted_data, baseline_schema)
                    validation_df = pd.DataFrame.from_dict(validation_results, orient="index")

                    st.write("Columns in Validation DataFrame:", validation_df.columns.tolist())

                    def color_valid(val):
                        if val == True:
                            return "background-color: #c8e6c9; color: #1b5e20;"  # Green ✅
                        elif val == False:
                            return "background-color: #ffcdd2; color: #b71c1c;"  # Red ❌
                        return ""

                    if "valid" in validation_df.columns:
                        st.dataframe(validation_df.style.map(color_valid, subset=["valid"]))
                    else:
                        st.warning("⚠️ 'valid' column missing in validation data.")

                st.download_button("📥 Download Validation Results", validation_df.to_csv().encode(), file_name="validation_results.csv")
