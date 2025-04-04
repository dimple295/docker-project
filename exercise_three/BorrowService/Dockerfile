# Use a base image with Python and necessary dependencies
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt


# Copy the application code
COPY . .

EXPOSE 6000


# Run the application
CMD ["python", "main.py"]


