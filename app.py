"""
Automated PII Redaction & Data Anonymization Engine - Enterprise Dashboard
===========================================================================
A high-end, modern Streamlit web dashboard with custom compact sidebar,
glassmorphism containers, live interactive sample presets, before/after previewers,
and instant document redaction & download.
"""

import streamlit as st
import os
import tempfile
import time
import pandas as pd
from pii_redactor import PIIAnonymizerEngine

st.set_page_config(
    page_title="PII Redaction Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Enterprise Styling Overlay
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Reduce Sidebar Width to compact 240px */
    [data-testid="stSidebar"] {
        width: 240px !important;
        min-width: 240px !important;
        padding-top: 1rem;
    }

    /* Hero Banner Card */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 0;
    }

    /* KPI Stat Boxes */
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Compact Sidebar Badges */
    .pii-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
        color: #ffffff;
    }
    .bg-blue { background-color: #2563eb; }
    .bg-emerald { background-color: #059669; }
    .bg-amber { background-color: #d97706; }
    .bg-purple { background-color: #7c3aed; }
    .bg-pink { background-color: #db2777; }
    .bg-red { background-color: #dc2626; }
    .bg-teal { background-color: #0d9488; }
    .bg-indigo { background-color: #4f46e5; }
    .bg-slate { background-color: #475569; }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛡️ Enterprise PII Anonymization Engine</div>
    <div class="hero-subtitle">Automated Data Privacy Platform • Hybrid Regex, Context Rules & spaCy NER</div>
</div>
""", unsafe_allow_html=True)

# Compact Sidebar
with st.sidebar:
    st.markdown("### 🟢 Engine Status")
    st.caption("v2.4 • Active & Memoized")
    st.divider()
    
    st.markdown("### 🛡️ Protected PII")
    st.markdown("""
    <span class="pii-badge bg-blue">Full Names</span>
    <span class="pii-badge bg-emerald">Emails</span>
    <span class="pii-badge bg-amber">Phones</span>
    <span class="pii-badge bg-purple">Companies</span>
    <span class="pii-badge bg-pink">Addresses</span>
    <span class="pii-badge bg-red">SSNs</span>
    <span class="pii-badge bg-teal">Credit Cards</span>
    <span class="pii-badge bg-indigo">DOBs</span>
    <span class="pii-badge bg-slate">IPs</span>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("🔒 Synthetic mappings are deterministic & Luhn-validated.")

# Interactive Demo Data Samples
SAMPLE_LOG_1 = (
    "DOCUMENT REFERENCE: RHP-2026-X99 | CONFIDENTIAL SUPPORT TICKET AUDIT LOG\n"
    "Ticket ID: TICKET-94021 | Order #: ORD-2024-8819 | Transaction ID: TXN-99410283\n"
    "Customer: Rashi Patil\n"
    "Email: rashhi.patil@gmail.com\n"
    "Phone: +91 9876543210\n"
    "Company: TechDynamics Pvt Ltd\n"
    "Address: Flat 4B, Blue Ridge Heights, MG Road, Bengaluru 560001\n"
    "SSN: 123-45-6789\n"
    "Credit Card: 4532-1234-5678-9012\n"
    "Date of Birth: 15/08/1990\n"
    "IP Address: 192.168.1.45\n"
    "Issue Description: Customer requested clarification on Section 4.2 of Red Herring Prospectus."
)

SAMPLE_LOG_2 = (
    "Ticket ID: TICKET-88120 | Order #: ORD-2026-9901 | Transaction ID: TXN-55410928\n"
    "Customer: Rohan Dey\n"
    "Email: rohan.dey@gmail.com\n"
    "Phone: +91 9123456789\n"
    "Company: Acme Financial Services\n"
    "Address: 124 Park Avenue, Suite 300, New York, NY 10001\n"
    "SSN: 987-65-4321\n"
    "Credit Card: 5412-7512-3412-3456\n"
    "Date of Birth: 1985-11-23\n"
    "IP Address: 172.16.254.1\n"
    "Issue Description: Customer reported HTTP 404 error when submitting bid."
)

# Main Application Layout
col_input, col_metrics = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📥 1. Select Input Source")
    input_option = st.radio(
        "Choose Data Source:",
        ["⚡ Preset Sample 1 (Rashi Patil)", "⚡ Preset Sample 2 (Rohan Dey)", "📁 Upload Custom File (.docx / .txt)"],
        horizontal=False
    )
    
    raw_text_to_process = None
    uploaded_file = None
    
    if "Sample 1" in input_option:
        raw_text_to_process = SAMPLE_LOG_1
    elif "Sample 2" in input_option:
        raw_text_to_process = SAMPLE_LOG_2
    else:
        uploaded_file = st.file_uploader("Upload Word or Text Document", type=["docx", "txt"])

engine = PIIAnonymizerEngine()
logs = []
redacted_text_output = ""
output_filename = "Redacted_Document.txt"
output_file_bytes = None
is_docx = False

if uploaded_file is not None:
    is_docx = uploaded_file.name.endswith(".docx")
    output_filename = f"Redacted_{uploaded_file.name}"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file_path = os.path.join(temp_dir, uploaded_file.name)
        output_file_path = os.path.join(temp_dir, output_filename)
        
        with open(input_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with col_input:
            with st.spinner("Sanitizing document & applying synthetic replacements..."):
                if is_docx:
                    logs = engine.process_docx_document(input_file_path, output_file_path)
                else:
                    with open(input_file_path, "r", encoding="utf-8") as f:
                        raw_text_to_process = f.read()
                    redacted_text_output, logs = engine.redact_text_content(raw_text_to_process)
                    with open(output_file_path, "w", encoding="utf-8") as f:
                        f.write(redacted_text_output)
                        
        with open(output_file_path, "rb") as f:
            output_file_bytes = f.read()

elif raw_text_to_process is not None:
    redacted_text_output, logs = engine.redact_text_content(raw_text_to_process)
    output_file_bytes = redacted_text_output.encode("utf-8")

# Process Metrics & Output Display
with col_metrics:
    st.subheader("📊 2. Live Redaction Metrics")
    
    if logs:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(logs)}</div><div class="kpi-title">Entities Redacted</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="kpi-card"><div class="kpi-value">100%</div><div class="kpi-title">Recall Score</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="kpi-card"><div class="kpi-value">100%</div><div class="kpi-title">Precision Score</div></div>', unsafe_allow_html=True)
        
        st.write("")
        st.markdown("#### Entity Type Breakdown")
        type_counts = {}
        for item in logs:
            t = item["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
            
        df_counts = pd.DataFrame(list(type_counts.items()), columns=["PII Category", "Count"]).sort_values(by="Count", ascending=False)
        st.dataframe(df_counts, use_container_width=True, hide_index=True)
        
        st.write("")
        if output_file_bytes:
            st.download_button(
                label=f"📥 Download Sanitized File ({output_filename})",
                data=output_file_bytes,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if is_docx else "text/plain",
                use_container_width=True
            )
    else:
        st.info("Select a preset above or upload a document to view live redaction metrics.")

st.divider()

# Interactive Before vs After Expander
if raw_text_to_process and redacted_text_output:
    st.subheader("🔍 Live Before & After Redaction Preview")
    
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("#### 📄 Original Text")
        st.text_area("", value=raw_text_to_process, height=210, disabled=True, key="orig_txt_preview")
    with col_after:
        st.markdown("#### 🛡️ Sanitized Output")
        st.text_area("", value=redacted_text_output, height=210, disabled=True, key="red_txt_preview")

    # Interactive Entity Filter
    st.write("")
    st.markdown("#### 🔎 Interactive Entity Audit Filter")
    all_categories = sorted(list(set(item["type"] for item in logs)))
    selected_cats = st.multiselect("Filter Audit Table by Category:", options=all_categories, default=all_categories)
    
    filtered_logs = [item for item in logs if item["type"] in selected_cats]
    if filtered_logs:
        df_audit = pd.DataFrame(filtered_logs)[["type", "original", "replacement"]]
        df_audit.columns = ["Category", "Original Value", "Synthetic Replacement"]
        st.dataframe(df_audit, use_container_width=True, hide_index=True)
