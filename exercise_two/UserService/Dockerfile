# Use Python 3.9 base image
FROM python:3.9


WORKDIR /app

# Copy code into the container
COPY . /app

# Install dependencies
RUN pip install pika flask flask_sqlalchemy psycopg2-binary requests

# Expose the port used by the UserService
EXPOSE 5002

# Run the application
CMD ["python", "main.py"]




