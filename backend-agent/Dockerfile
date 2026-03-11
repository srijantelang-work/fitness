# Use the official lightweight Python image.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=True
# Cloud Run dynamically provides the $PORT environment variable. Default to 8080 for local testing.
ENV PORT=8080

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Run the web service on container startup using Uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
