# Intelligent Resume Prioritization System (Streamlit App)

This project is a web application built with **Streamlit** that demonstrates an **Intelligent Resume Prioritization System**. It allows HR professionals to input job descriptions and candidate resumes, which are then processed and ranked using **Machine Learning** techniques implemented in **Python**. The system is designed for easy deployment via **Docker** and can be integrated with **Vertex AI** for scalable ML model serving and **RPA** for automated resume ingestion.

## Technologies Used

* **Python:** The core programming language for the entire application, including the Streamlit UI, ML models, and data processing.
* **Streamlit:** Used for rapidly building the interactive web user interface, allowing data scientists to create powerful web apps purely in Python.
* **Machine Learning (ML):** Implemented for key functionalities:
    * **Resume Parsing:** Extracts structured information (skills, experience, contact) from raw resume text and uploaded PDF/DOCX files.
    * **Semantic Skill Matching:** Utilizes pre-trained language models (Sentence Transformers) to understand the contextual similarity between skills in resumes and job descriptions.
    * **Ranking Algorithm:** A weighted scoring system that combines skill match, estimated experience, and education relevance to prioritize candidates.
    * **NLP Libraries:** `NLTK` for text cleaning (stopwords, lemmatization), `spaCy` (for potential future advanced entity extraction), and `Hugging Face Transformers` (for sentence embeddings).
    * **`pdfminer.six` and `python-docx`:** For extracting text content from PDF and DOCX files, respectively.
* **Vertex AI (Integration Capability):** While the core ML models run within the Streamlit app for this demo, in a production environment, heavy ML models (like larger semantic embedding models or complex ranking models) would be deployed and served via **Vertex AI Endpoints** on Google Cloud Platform. This ensures scalability, managed model deployment, and MLOps capabilities.
* **RPA (Robotic Process Automation - Conceptual Integration):** RPA agents can be integrated to automate the initial ingestion of resumes from various shared locations (e.g., network drives, email attachments, Applicant Tracking Systems exports) into a central storage like Google Cloud Storage, which this application could then fetch and process.
* **Docker:** Used for containerizing the application, ensuring consistent and reproducible deployment across different environments.
* **Google Cloud Run (Deployment Target):** A serverless platform for deploying containerized applications, providing scalability and ease of management.

## Features

* **Interactive UI:** User-friendly interface for inputting job descriptions and resumes.
* **Flexible Resume Input:** Supports pasting raw resume texts (separated by `---NEW RESUME---`) or uploading multiple PDF/DOCX files.
* **Intelligent Parsing:** Extracts key information from resumes to facilitate matching.
* **ML-Powered Ranking:** Ranks candidates based on their relevance to the job description, providing a score and skill match percentage.
* **Detailed Insights:** Allows users to view the raw content and parsed data for each ranked resume.
* **Real-time Feedback:** Provides immediate ranked results and processing status messages.
* **Containerized Deployment:** Ready to be deployed as a Docker container to cloud services.

## Project Structure