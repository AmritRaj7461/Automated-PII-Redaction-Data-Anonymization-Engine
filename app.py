"""
PII Redaction Engine - Web Dashboard
------------------------------------
A modern Streamlit Web Application allowing users to upload .docx / .txt documents,
perform live PII redaction, inspect entity detection metrics, and download redacted DOCX outputs.
"""

import streamlit as st
import os
import tempfile
from pii_redactor import PIIAnonymizerEngine

st.set_page_config(
    page_title="PII Redaction Tool",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Automated PII Redaction & Anonymization Tool")
st.markdown(
    "Upload any Word document (`.docx`) or text log (`.txt`) to automatically detect and replace sensitive "
    "personally identifiable information (Full Names, Emails, Phones, Companies, Addresses, SSNs, Credit Cards, DOBs, IPs) "
    "with realistic synthetic data."
)

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader("Choose a .docx or .txt file", type=["docx", "txt"])

if uploaded_file is not None:
    engine = PIIAnonymizerEngine()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file_path = os.path.join(temp_dir, uploaded_file.name)
        output_file_path = os.path.join(temp_dir, f"Redacted_{uploaded_file.name}")
        
        with open(input_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Processing document and redacting PII..."):
            if uploaded_file.name.endswith(".docx"):
                logs = engine.process_docx_document(input_file_path, output_file_path)
            else:
                with open(input_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                redacted_content, logs = engine.redact_text_content(content)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(redacted_content)

        with col2:
            st.subheader("✅ Redaction Summary")
            st.metric(label="Total PII Entities Redacted", value=len(logs))
            
            # Count by type
            type_counts = {}
            for item in logs:
                t = item["type"]
                type_counts[t] = type_counts.get(t, 0) + 1
                
            st.write("**Entity Type Breakdown:**")
            st.json(type_counts)

        st.divider()
        
        # Download Section
        st.subheader("📥 Download Redacted Document")
        with open(output_file_path, "rb") as f:
            file_bytes = f.read()
            
        st.download_button(
            label=f"⬇️ Download Redacted {uploaded_file.name}",
            data=file_bytes,
            file_name=f"Redacted_{uploaded_file.name}",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if uploaded_file.name.endswith(".docx") else "text/plain"
        )
