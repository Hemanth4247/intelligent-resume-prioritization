# Use a stable, lightweight Python base image.
FROM python:3.9-slim-buster

# Set the working directory inside the container.
WORKDIR /app

# Copy your project's requirements.txt into the container.
COPY requirements.txt .

# --- START CRITICAL UPDATED INSTALLATION SECTION ---
# Install PyTorch first, specifically the CPU-only version, from PyTorch's stable URL.
# This is more robust than relying on pip's default resolution, especially for large packages.
# Make sure these versions (2.0.0, 0.15.2, 2.0.2) are compatible if you used a different torch version locally.
# If this specific version fails, check https://pytorch.org/get-started/locally/ for the latest CPU-only pip command for Linux.
RUN pip install --no-cache-dir \
    torch==2.0.0+cpu \
    torchvision==0.15.2+cpu \
    torchaudio==2.0.2+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Now, install the rest of your dependencies from requirements.txt.
# This command should run smoothly as torch is already handled.
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data required by your TextCleaner or other NLTK uses.
# 'punkt' is commonly used for tokenization, 'stopwords' for cleaning.
RUN python -m nltk.downloader punkt stopwords

# Download the default SpaCy model used by SpaCy-based components.
# 'en_core_web_sm' is the small English model.
RUN python -m spacy download en_core_web_sm
# --- END CRITICAL UPDATED INSTALLATION SECTION ---

# Copy the entire contents of your local project directory into the container.
COPY . .

# Declare that the container will listen for network traffic on port 8080.
EXPOSE 8080

# Command to run when the container starts (starts your Streamlit app).
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]