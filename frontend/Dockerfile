FROM python:3.10-slim

WORKDIR /workspace

# Install requirements for the UI layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend code
COPY app.py .

# Expose the Streamlit default port
EXPOSE 8501

# Run Streamlit with flags to handle container networking gracefully
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]