
import json
import pika
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from threading import Thread  # For concurrent tasks
import requests
from flask import jsonify



BOOK_SERVICE_URL =  'http://book-service:5006'


# Get RabbitMQ and PostgreSQL credentials from environment variables
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
rabbitmq_pass = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')

# Set up Flask and SQLAlchemy for database interaction
app = Flask(__name__)

# PostgreSQL database connection settings
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database models
class Student(db.Model):
    __tablename__ = 'users'
    studentid = db.Column(db.String(20), primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Book(db.Model):
    __tablename__ = 'books'
    bookid = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

class BorrowRequest(db.Model):
    __tablename__ = 'borrow_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('users.studentid'), nullable=False)
    book_id = db.Column(db.String(20), db.ForeignKey('books.bookid'), nullable=False)
    date_returned = db.Column(db.Date, nullable=False)

# Create tables in the database
with app.app_context():
    db.create_all()

# Establish connection to RabbitMQ
def setup_rabbitmq():
    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672, '/', credentials))
        channel = connection.channel()
        channel.queue_declare(queue='borrow_book')  # Declare the queue to ensure it exists
        return channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}", flush=True)
        return None

# Handle borrow requests from RabbitMQ
def callback(ch, method, properties, body):
    borrow_data = json.loads(body)
    student_id = borrow_data.get('student_id')
    book_id = borrow_data.get('book_id')
    date_returned = borrow_data.get('date_returned')
    print(borrow_data, flush=True)

    borrow_request = BorrowRequest(student_id=student_id, book_id=book_id, date_returned=date_returned)
    with app.app_context():
        db.session.add(borrow_request)
        db.session.commit()
    print(f"Borrow request saved: Student {student_id} borrowed Book {book_id} until {date_returned}", flush=True)

# Start listening for messages from RabbitMQ
def start_borrow_service():
    channel = setup_rabbitmq()
    if channel:
        print('Waiting for borrow requests...', flush=True)
        channel.basic_consume(queue='borrow_book', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

# Define a route to get all books borrowed by a specific user
@app.route('/borrowed_books/<string:student_id>', methods=['GET'])
def get_borrowed_books(student_id):
    books_response = requests.get(f"{BOOK_SERVICE_URL}/books/all", headers={"Content-Type": "application/json"})
    if books_response.status_code != 200:
        return jsonify({"error": "Failed to fetch books from BookService"}), 500
    
    # Convert the books response to a dictionary for easier lookups
    books_data = {book['bookid']: book for book in books_response.json()}

    # Step 2: Query borrow records for the student from BorrowRequest table
    borrowed_records = (
        db.session.query(BorrowRequest.book_id, BorrowRequest.date_returned)
        .filter(BorrowRequest.student_id == student_id)
        .all()
    )

    # Step 3: Combine borrow records with book details
    result = []
    for book_id, date_returned in borrowed_records:
        book = books_data.get(book_id)
        if book:
            result.append({
                "title": book["title"],
                "author": book["author"],
                "date_returned": date_returned
            })
        else:
            # Handle cases where book details are not found
            result.append({
                "title": "Unknown",
                "author": "Unknown",
                "date_returned": date_returned
            })
    
    return jsonify(result)

# Run Flask and RabbitMQ listener concurrently
if __name__ == "__main__":
    Thread(target=start_borrow_service).start()  # Start RabbitMQ listener in a separate thread
    app.run(host='0.0.0.0', port=6000,debug=True)  # Run Flask app
