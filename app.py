import streamlit as st
st.set_page_config(layout="wide", page_title="Intelligent Resume Prioritization")

import pandas as pd
import os
import io
import uuid
import re

# Import your core logic modules from src
from src.ml.resume_parser import ResumeParser
from src.ml.skill_matcher import SkillMatcher
from src.ml.ranker import ResumeRanker
from src.nlp.text_cleaner import TextCleaner
# from src.utils.gcp_utils import download_blob_to_memory # Uncomment if you enable GCS fetching

# --- Initialize Core Components (Load models/resources once) ---
# Use st.cache_resource to load heavy models and NLP components only once across runs
@st.cache_resource
def load_ml_components():
    """Loads and initializes ML/NLP components.
    This function uses Streamlit's caching to ensure components are loaded only once
    when the app starts, improving performance.
    """
    st.write("Initializing ML components... (This runs once on app startup)")
    parser = ResumeParser()
    # The SkillMatcher and Ranker could internally make calls to Vertex AI Endpoints
    # For this deployable example, they operate locally.
    matcher = SkillMatcher() # This will attempt to load a Sentence Transformer model
    ranker = ResumeRanker()
    cleaner = TextCleaner() # This will attempt to load NLTK data and SpaCy model
    return parser, matcher, ranker, cleaner

parser, matcher, ranker, cleaner = load_ml_components()

# --- Utility Function for Job Description Processing ---
def process_job_description(job_description_text: str) -> dict:
    """
    Processes the job description to extract requirements.
    In a real application, this would use more sophisticated NLP/ML
    (e.g., Named Entity Recognition for specific skills, experience ranges).
    """
    lower_case_jd = job_description_text.lower()

    # Simple extraction of required skills (can be expanded with more NLP)
    # This regex is a basic example; a real system would use a pre-trained NER model
    # or a comprehensive skill taxonomy.
    job_skills_keywords = re.findall(r'\b(python|machine learning|data science|rpa|vertex ai|tensorflow|pytorch|sql|java|javascript|react|cloud|aws|azure|gcp|nlp|deep learning|statistics|docker|kubernetes|ai|ml|big data|spark|hadoop)\b', lower_case_jd)

    # Simple estimation of min experience (e.g., looking for "X years experience")
    min_experience_match = re.search(r'(\d+)\+\s*years?\s*experience', lower_case_jd)
    min_experience_years = int(min_experience_match.group(1)) if min_experience_match else 0

    # Simple extraction of required education keywords
    required_education_keywords = re.findall(r'\b(bachelor\'?s|master\'?s|ph\.?d\.?|degree|b\.\s*tech|m\.\s*tech|mba|computer science|engineering|statistics|mathematics)\b', lower_case_jd)

    return {
        "required_skills": list(set(job_skills_keywords)), # Get unique skills
        "min_experience_years": min_experience_years,
        "required_education": list(set(required_education_keywords))
    }

# --- Streamlit UI Layout ---
st.title("🎯 Intelligent Resume Prioritization System")
st.markdown("""
    This application helps HR teams quickly screen and rank resumes based on job requirements.
    It leverages **Python** for core logic, **Machine Learning** for intelligent matching,
    and can integrate with **Vertex AI** for scalable model serving and **RPA** for automated ingestion.
""")

# --- Job Description Input ---
st.header("1. Enter Job Description")
job_description = st.text_area(
    "Paste the full job description here:",
    height=200,
    key="jd_input",
    placeholder="E.g., 'Seeking a Senior Data Scientist with 5+ years experience in Python, Machine Learning, and Vertex AI. Master's degree in CS preferred...'"
)
# Process JD immediately to show detected requirements
job_requirements = process_job_description(job_description)

st.markdown(f"""
    **Detected Job Requirements:**
    - **Skills:** {', '.join(job_requirements['required_skills']) if job_requirements['required_skills'] else 'None detected'}
    - **Min Experience:** {job_requirements['min_experience_years']} years
    - **Education:** {', '.join(job_requirements['required_education']) if job_requirements['required_education'] else 'None detected'}
""")

# --- Resume Input ---
st.header("2. Upload/Paste Resumes")
resume_upload_method = st.radio(
    "Choose method to input resumes:",
    ("Paste Text (for quick demo)", "Upload Files (PDF/DOCX)"), # Removed GCS option for simplicity in this single file
    key="upload_method_radio"
)

raw_resumes_text = ""
uploaded_files = []

if resume_upload_method == "Paste Text (for quick demo)":
    raw_resumes_text = st.text_area(
        "Paste resume texts here. Use '---NEW RESUME---' on a new line to separate multiple resumes.",
        height=300,
        key="raw_resumes_text_input",
        placeholder="""John Doe
Contact: john.doe@example.com | 123-456-7890
Summary: Experienced Data Scientist with 5 years in Machine Learning and Python.
Experience: Google - Data Scientist (2020-Present) Developed ML models using TensorFlow and deployed on Vertex AI.
---NEW RESUME---
Jane Smith
Contact: jane.smith@example.com
Summary: Software Engineer with 7 years in Java and SQL.
Experience: Amazon - Software Engineer (2018-Present) Developed backend systems using Java and Spring.
Education: B.Tech in Computer Science from IIT.
"""
    )
elif resume_upload_method == "Upload Files (PDF/DOCX)":
    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX files (multiple allowed):",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    st.info("Note: Full text extraction from PDF/DOCX is handled by `pdfminer.six` and `python-docx` in the backend.")


# --- Process Button ---
st.markdown("---")
if st.button("🚀 Process Resumes", type="primary", use_container_width=True):
    if not job_description.strip():
        st.error("Please enter a job description before processing.")
        st.stop()
    if not raw_resumes_text.strip() and not uploaded_files:
        st.warning("No resumes provided. Please paste text or upload files.")
        st.stop()

    processed_resumes = []

    # Process pasted text resumes
    if raw_resumes_text.strip():
        individual_resumes = raw_resumes_text.split('---NEW RESUME---')
        for i, text in enumerate(individual_resumes):
            text = text.strip()
            if text:
                parsed_data = parser.parse_text(text)
                processed_resumes.append({
                    "resume_id": f"pasted_resume_{i+1}",
                    "original_source": "Pasted Text",
                    "parsed_data": parsed_data
                })

    # Process uploaded files
    for uploaded_file in uploaded_files:
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            resume_text = ""
            if file_extension == ".pdf":
                # Pass BytesIO object to parser
                resume_text = parser.parse_pdf(io.BytesIO(uploaded_file.getvalue()))
            elif file_extension == ".docx":
                # Pass BytesIO object to parser
                resume_text = parser.parse_docx(io.BytesIO(uploaded_file.getvalue()))
            else: # Assume .txt or similar
                resume_text = uploaded_file.getvalue().decode('utf-8', errors='ignore')

            if resume_text:
                parsed_data = parser.parse_text(resume_text)
                processed_resumes.append({
                    "resume_id": str(uuid.uuid4()),
                    "original_source": uploaded_file.name,
                    "parsed_data": parsed_data
                })
        except Exception as e:
            st.error(f"Error processing '{uploaded_file.name}': {e}. Ensure it's a valid PDF/DOCX or plain text.")
            continue

    if not processed_resumes:
        st.warning("No valid resumes were successfully processed from your input. Please check the format.")
    else:
        st.success(f"Successfully processed {len(processed_resumes)} resumes.")
        with st.spinner("Ranking candidates..."):
            # Rank the parsed resumes using the ML models
            # This call can implicitly trigger API calls to Vertex AI Endpoints if configured in matcher/ranker
            ranked_candidates = ranker.rank_resumes(processed_resumes, job_requirements, matcher)

        st.subheader("📊 Ranked Candidates")
        if ranked_candidates:
            # Prepare data for display
            display_data = []
            for cand in ranked_candidates:
                display_data.append({
                    "Rank": ranked_candidates.index(cand) + 1,
                    "Score (0-100)": cand['score'],
                    "Skill Match (%)": cand['skill_match_score'],
                    "Resume ID": cand['resume_id'],
                    "Source File": cand['original_source'],
                    "Extracted Skills": ", ".join(cand['parsed_data']['skills']),
                    "Estimated Experience": f"{ranker.estimate_experience_years(cand['parsed_data'].get('experience', [])):.1f} years", # Show estimated years
                    "Education KWs": ", ".join(cand['parsed_data']['education']), # Use 'education' from parsed_data
                    "Email": cand['parsed_data']['contact']['email'] or 'N/A',
                    "Phone": cand['parsed_data']['contact']['phone'] or 'N/A'
                })

            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, height=300) # Fixed height for better table display

            st.markdown("---")
            st.subheader("🔍 Detailed Resume Insights")
            # --- FIX APPLIED HERE ---
            for cand_display in display_data: # Iterate over display_data which contains the 'Rank'
                with st.expander(f"Candidate {cand_display['Rank']} (ID: {cand_display['Resume ID']}) - Score: {cand_display['Score (0-100)']}/100 - {cand_display['Source File']}"):
                    st.json({
                        "resume_id": cand_display['Resume ID'], # Use key from display_data
                        "score": cand_display['Score (0-100)'], # Use key from display_data
                        "skill_match_score": cand_display['Skill Match (%)'], # Use key from display_data
                        "estimated_experience_years": ranker.estimate_experience_years(next((rc['parsed_data'] for rc in ranked_candidates if rc['resume_id'] == cand_display['Resume ID']), {}).get('experience', [])), # Retrieve original parsed_data for experience
                        "parsed_data": next((rc['parsed_data'] for rc in ranked_candidates if rc['resume_id'] == cand_display['Resume ID']), {}) # Retrieve original parsed_data
                    })
                    st.markdown("**Raw Content:**")
                    st.text(next((rc['parsed_data'] for rc in ranked_candidates if rc['resume_id'] == cand_display['Resume ID']), {}).get('rawContent', ''))
            # --- END FIX ---
        else:
            st.warning("No candidates were ranked. Ensure resumes contain relevant information.")

st.markdown("---")
st.caption("Developed with Python, Machine Learning, and integration potential with Vertex AI and RPA.")