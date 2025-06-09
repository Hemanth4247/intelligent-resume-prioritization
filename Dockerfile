# Use a stable, lightweight Python base image.
# This is the foundation: it includes Python 3.9 and basic Linux utilities.
FROM python:3.9-slim-buster

# Set the working directory inside the container.
# All subsequent commands (COPY, RUN, CMD) will be executed relative to this directory.
# So, '/app' inside the container will contain your project code.
WORKDIR /app

# Copy your project's 'requirements.txt' file into the container's '/app' directory.
# We do this first so Docker can cache this step. If only code changes,
# it won't reinstall dependencies unnecessarily.
COPY requirements.txt .

# Install all Python dependencies listed in 'requirements.txt'.
# '--no-cache-dir' helps keep the final Docker image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire contents of your local project directory (where this Dockerfile is)
# into the container's '/app' directory.
# The first '.' refers to your local current directory.
# The second '.' refers to the WORKDIR '/app' inside the container.
COPY . .

# Declare that the container will listen for network traffic on port 8080.
# Cloud Run expects applications to listen on port 8080 by default.
EXPOSE 8080

# This is the command that Docker will run when the container starts.
# It starts your Streamlit application.
# "streamlit run app.py": Tells Streamlit to execute your main app file.
# "--server.port 8080": Forces Streamlit to listen on port 8080.
# "--server.address 0.0.0.0": Makes the Streamlit app accessible from outside the container.
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]