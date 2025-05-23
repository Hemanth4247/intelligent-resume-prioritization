# This Dockerfile defines the steps to build a Docker image for your Streamlit application.
# It uses a multi-stage build for a smaller final image.

# Stage 1: Build environment for dependencies and model downloads
FROM python:3.9-slim-buster as build-env

# Set working directory
WORKDIR /app

# Install system dependencies needed for NLP libraries and PDF/DOCX processing
# These are crucial for libraries like pdfminer.six and spacy
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libgl1-mesa-glx \
    libgirepository1.0-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/archives/*

# Copy the requirements file into the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (only once during image build)
# These are necessary for text_cleaner.py
RUN python -m nltk.downloader stopwords wordnet punkt averaged_perceptron_tagger

# Download SpaCy model (only once during image build)
# This is necessary for text_cleaner.py if you enable entity extraction
RUN python -m spacy download en_core_web_sm

# Download Sentence Transformer model (only once during image build)
# This is necessary for skill_matcher.py
RUN pip install sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Stage 2: Final lightweight image for production
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy installed dependenci
es and downloaded models from the build-env stage
COPY --from=build-env /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build-env /root/.cache/torch /root/.cache/torch # For Sentence Transformer model cache
COPY --from=build-env /root/nltk_data /usr/local/share/nltk_data # For NLTK data
COPY --from=build-env /usr/local/lib/python3.9/site-packages/spacy/data/en_core_web_sm /usr/local/lib/python3.9/site-packages/spacy/data/en_core_web_sm # For SpaCy model

# Copy the application code
COPY . /app

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
# --server.port=8501: Ensures Streamlit listens on this port
# --server.enableCORS=false: Disables CORS protection (useful for some deployments)
# --server.enableXsrfProtection=false: Disables XSRF protection (useful for some deployments)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]