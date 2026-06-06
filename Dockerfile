# Use an official lightweight Python image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /workspace

# Install system dependencies required for certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code and documentation assets
COPY app/ ./app/
COPY docs/ ./docs/
COPY main.py .

# Expose the FastAPI default port
EXPOSE 8000

# Run the backend application
CMD ["python", "main.py"]