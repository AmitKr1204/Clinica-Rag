import streamlit as st
import requests
import json
from requests.auth import HTTPBasicAuth
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Set Page Config
st.set_page_config(
    page_title="Clinica-RAG | Clinical AI Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design System / CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus+Jakarta Sans', sans-serif;
    }
    
    /* Clean Hero Card */
    .hero-banner {
        background: linear-gradient(135deg, #0e7490 0%, #0369a1 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(14, 116, 144, 0.2);
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        color: #ffffff !important;
    }
    .hero-banner p {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        opacity: 0.9;
        color: #e0f2fe;
    }

    /* Content Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    /* Source Badges */
    .source-badge {
        display: inline-block;
        background-color: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* History Record Card */
    .record-box {
        border-left: 4px solid #0284c7;
        background-color: #f8fafc;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 20px;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Status Pill */
    .role-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        background-color: #e0f2fe;
        color: #0369a1;
        letter-spacing: 0.05em;
    }

    /* Medical Disclaimer Footer */
    .disclaimer-box {
        font-size: 0.8rem;
        color: #64748b;
        background-color: #f8fafc;
        border: 1px dashed #cbd5e1;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# Initial State Management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "auth" not in st.session_state:
    st.session_state.auth = None

# API Functions (100% Unchanged logic)
def signup_user(username, password, role):
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json={"username": username, "password": password, "role": role}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "FastAPI Server unreachable. Please ensure the backend is running."}

def authenticate_user(username, password):
    try:
        response = requests.get(
            f"{API_URL}/auth/login",
            auth=HTTPBasicAuth(username, password)
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "FastAPI Server unreachable. Please ensure the backend is running."}

def upload_report(auth, files):
    try:
        headers = {'accept': 'application/json'}
        files_data = [('files', (file.name, file.getvalue(), file.type)) for file in files]
        response = requests.post(
            f"{API_URL}/reports/upload",
            auth=auth,
            files=files_data,
            headers=headers
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

def get_diagnosis(auth, doc_id, question):
    try:
        data = {
            'doc_id': doc_id,
            'question': question
        }
        response = requests.post(
            f"{API_URL}/diagnosis/from_report",
            auth=auth,
            data=data
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

def get_doctor_diagnosis(auth, patient_name):
    try:
        response = requests.get(
            f"{API_URL}/diagnosis/by_patient_name",
            auth=auth,
            params={'patient_name': patient_name}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

# Sidebar - Brand & Session Navigation
with st.sidebar:
    st.markdown("### 🩺 **Clinica-RAG**")
    st.caption("AI-Powered Clinical Analysis & Retrieval")
    st.markdown("---")

    if st.session_state.logged_in:
        st.markdown(f"👤 **Current User:** `{st.session_state.username}`")
        st.markdown(f"🏷️ **Access Level:** <span class='role-pill'>{st.session_state.role}</span>", unsafe_allow_html=True)
        st.markdown("")
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.auth = None
            if 'doc_id' in st.session_state:
                del st.session_state.doc_id
            st.rerun()
    else:
        auth_mode = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        
        if auth_mode == "Login":
            st.markdown("#### Portal Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Authenticate", use_container_width=True, type="primary"):
                if login_username and login_password:
                    with st.spinner("Verifying credentials..."):
                        status_code, data = authenticate_user(login_username, login_password)
                        if status_code == 200:
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.session_state.role = data["role"]
                            st.session_state.auth = HTTPBasicAuth(login_username, login_password)
                            st.rerun()
                        else:
                            st.error(f"{data.get('detail', 'Authentication failed')}")
                else:
                    st.warning("Please provide both username and password.")

        else:
            st.markdown("#### Create Account")
            signup_username = st.text_input("Username", key="signup_username")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_role = st.selectbox("Role", ["patient", "doctor"], key="signup_role")
            if st.button("Register", use_container_width=True, type="primary"):
                if signup_username and signup_password:
                    with st.spinner("Registering user..."):
                        status_code, data = signup_user(signup_username, signup_password, signup_role)
                        if status_code == 200:
                            st.success("Account created successfully! Please proceed to Login.")
                        elif status_code == 400:
                            st.error(f"{data.get('detail', 'User already exists')}")
                        else:
                            st.error(f"{data.get('detail', 'Signup failed')}")
                else:
                    st.warning("Please fill in all registration fields.")

# Top Hero Section
st.markdown("""
<div class="hero-banner">
    <h1>CuraMind AI — Clinical Diagnostic RAG</h1>
    <p>Context-aware pathology report analysis powered by LangChain, Pinecone Vector Storage, and Gemini/Groq Inference.</p>
</div>
""", unsafe_allow_html=True)

# Main Workspace
if not st.session_state.logged_in:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("👋 **Welcome to the Clinica-RAG portal.** Please log in or create an account using the left sidebar to access clinical diagnostic tools.")
        
        st.markdown("### Architecture Highlights")
        feat_col1, feat_col2 = st.columns(2)
        with feat_col1:
            st.markdown("""
            * **Cloud Vector Store:** Scaled document embeddings using Pinecone Serverless.
            * **Zero-Retention Processing:** Real-time chunking and ephemeral token synthesis.
            """)
        with feat_col2:
            st.markdown("""
            * **Role-Based Workflows:** Distinct interfaces tailored for patients and clinical providers.
            * **Verifiable Grounding:** Context citations matched to exact source pages.
            """)
            
    with col2:
        st.markdown("""
        <div style="background-color: #f1f5f9; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">
            <h4 style="margin-top:0;">Secure Gateway</h4>
            <p style="font-size:0.85rem; color:#475569;">All interactions are protected with HTTP Basic Authentication and RBAC endpoints backed by MongoDB.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Patient Dashboard
    if st.session_state.role == "patient":
        st.subheader("Patient Diagnostic Suite")
        
        tab_upload, tab_diagnose = st.tabs(["📤 1. Ingest Medical Reports", "🔍 2. AI Synthesis & Diagnosis"])

        with tab_upload:
            st.markdown("Upload clinical documentation (bloodwork, discharge summaries, imaging reports) in PDF or TXT format.")
            with st.form("upload_form", clear_on_submit=False):
                uploaded_files = st.file_uploader(
                    "Select Medical Reports",
                    type=["pdf", "txt"],
                    accept_multiple_files=True,
                    help="Upload one or multiple PDF/TXT files"
                )
                upload_submitted = st.form_submit_button("⚡ Ingest & Index Documents", type="primary")

                if upload_submitted:
                    if uploaded_files:
                        with st.spinner("Extracting text, computing vector embeddings, and updating Pinecone..."):
                            status_code, data = upload_report(st.session_state.auth, uploaded_files)
                            if status_code == 200:
                                st.session_state.doc_id = data['doc_id']
                                st.success(f"Processing complete! Attached Document Session ID:")
                                st.code(data['doc_id'], language="text")
                                st.caption("Proceed to tab '2. AI Synthesis & Diagnosis' to run queries.")
                            else:
                                st.error(f"Upload failed: {data.get('detail', 'Unknown error')}")
                    else:
                        st.warning("Please attach at least one valid file.")

        with tab_diagnose:
            default_doc_id = st.session_state.get('doc_id', '')
            
            with st.form("diagnosis_form"):
                diag_col1, diag_col2 = st.columns([1, 2])
                with diag_col1:
                    diagnosis_doc_id = st.text_input(
                        "Document Session ID",
                        value=default_doc_id,
                        placeholder="e.g. 59b6...",
                        help="The unique ID generated upon uploading your reports."
                    )
                with diag_col2:
                    diagnosis_question = st.text_input(
                        "Diagnostic Query",
                        value="Please provide a concise clinical breakdown and findings based on my report."
                    )
                
                diagnosis_submitted = st.form_submit_button("Generate AI Diagnostic Report", type="primary")

            if diagnosis_submitted:
                if not diagnosis_doc_id:
                    st.warning("A Document Session ID is required to query the knowledge store.")
                else:
                    with st.spinner("Retrieving semantic matches and synthesizing insights..."):
                        status_code, data = get_diagnosis(
                            st.session_state.auth,
                            diagnosis_doc_id,
                            diagnosis_question
                        )
                        if status_code == 200:
                            st.markdown("---")
                            st.markdown("### 📋 Clinical Diagnostic Summary")
                            
                            # Answer Box
                            st.markdown(f"""
                            <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                                {data.get("diagnosis", "No diagnosis provided.")}
                            </div>
                            """, unsafe_allow_html=True)

                            # Sources Badges
                            st.markdown("##### 📌 Grounded Source Documents")
                            sources = data.get("sources", [])
                            if sources:
                                badges_html = "".join([f"<span class='source-badge'>📄 {s}</span>" for s in sources if s])
                                st.markdown(badges_html, unsafe_allow_html=True)
                            else:
                                st.caption("No specific source attachments returned.")
                        else:
                            st.error(f"Diagnosis Query Failed: {data.get('detail', 'Unknown error')}")

    # Doctor Dashboard
    elif st.session_state.role == "doctor":
        st.subheader("Physician Diagnostic Review Console")
        st.caption("Inspect patient diagnostic logs, temporal progression, and historical inferences.")

        with st.form("doctor_form"):
            col_search, col_btn = st.columns([3, 1])
            with col_search:
                patient_name_input = st.text_input("Lookup Patient Username", placeholder="e.g. john_doe", label_visibility="collapsed")
            with col_btn:
                view_submitted = st.form_submit_button("Retrieve Records", use_container_width=True, type="primary")

        if view_submitted:
            if not patient_name_input.strip():
                st.warning("Please input a valid patient username.")
            else:
                with st.spinner(f"Querying diagnostic history for '{patient_name_input}'..."):
                    status_code, data = get_doctor_diagnosis(st.session_state.auth, patient_name_input)
                    if status_code == 200:
                        st.markdown(f"#### Diagnostic Log: **{patient_name_input}** ({len(data)} total records)")
                        st.markdown("---")
                        
                        if not data:
                            st.info("No prior diagnosis records found for this patient.")
                        else:
                            for idx, record in enumerate(data, start=1):
                                formatted_date = datetime.datetime.fromtimestamp(record['timestamp']).strftime('%b %d, %Y - %H:%M:%S')
                                
                                with st.container():
                                    st.markdown(f"""
                                    <div class="record-box">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                            <span style="font-weight:700; color:#0f172a;">Record #{idx} | Document ID: <code>{record['doc_id']}</code></span>
                                            <span style="color:#64748b; font-size:0.85rem;">🕒 {formatted_date}</span>
                                        </div>
                                        <div style="margin-bottom: 12px; font-size: 0.95rem; color:#334155;">
                                            <strong>Patient Inquiry:</strong> <em>"{record['question']}"</em>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    with st.expander("🔬 View Model Synthesis & Sources", expanded=True):
                                        st.markdown(record['answer'])
                                        st.markdown("---")
                                        if record.get('sources'):
                                            st.markdown("**Referenced Sources:**")
                                            badges_html = "".join([f"<span class='source-badge'>📄 {s}</span>" for s in record['sources'] if s])
                                            st.markdown(badges_html, unsafe_allow_html=True)
                                        else:
                                            st.caption("No individual sources logged.")
                                    st.markdown("")
                    else:
                        st.error(f"Failed to fetch records: {data.get('detail', 'Unknown error')}")

    else:
        st.warning("Your role is not recognized. Please contact system administration.")

# Clinical Disclaimer Footer
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ Clinical Safety Disclaimer:</strong> This platform utilizes retrieval-augmented AI systems intended strictly for clinical decision support and patient reference. It does not replace professional diagnostic judgment, physician consultations, or accredited laboratory testing.
</div>
""", unsafe_allow_html=True)