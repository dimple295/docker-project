# Use Python 3.9 base image
FROM python:3.9


WORKDIR /app

# Copy code into the container
COPY . /app

# Install dependencies
RUN pip install flask flask_sqlalchemy psycopg2-binary pika

# Expose the port used by the UserService
EXPOSE 5006

# Run the application
CMD ["python", "main.py"]

