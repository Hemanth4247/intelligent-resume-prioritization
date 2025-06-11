# Use a stable, lightweight Python base image.
FROM python:3.9-slim-buster

# Set the working directory inside the container.
WORKDIR /app

# Copy your project's requirements.txt into the container.
COPY requirements.txt .

# --- START CRITICAL UPDATED INSTALLATION SECTION ---
# Install PyTorch first, specifically the CPU-only version, using the official recommended method.
# This command was directly obtained from pytorch.org for Stable, Linux, Pip, Python, CPU.
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Now, install the rest of your dependencies from requirements.txt.
# This command should run smoothly as torch is already handled.
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data required by your TextCleaner or other NLTK uses.
RUN python -m nltk.downloader punkt stopwords

# Download the default SpaCy model used by SpaCy-based components.
RUN python -m spacy download en_core_web_sm
# --- END CRITICAL UPDATED INSTALLATION SECTION ---

# Copy the entire contents of your local project directory into the container.
COPY . .

# Declare that the container will listen for network traffic on port 8080.
EXPOSE 8080

# Command to run when the container starts (starts your Streamlit app).
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]