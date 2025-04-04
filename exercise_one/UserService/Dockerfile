# Base image for Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5002 for the service
EXPOSE 5002

# Command to run the Flask application
CMD ["python", "main.py"]
