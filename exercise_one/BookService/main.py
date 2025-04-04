from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

# Environment variables for database connection
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

# Initialize the Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Book model
class Book(db.Model):
    __tablename__ = 'books'

    bookid = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
   

    def to_dict(self):
        return {
            "bookid": self.bookid,
            "title": self.title,
            "author": self.author,
            
        }

# Create all tables (will create the books table)
with app.app_context():
    db.create_all()

# Routes for BookService

# CREATE a new book
@app.route('/books/add', methods=['POST'])
def create_book():
    data = request.json
    book = Book(
        bookid=data['bookid'],
        title=data['title'],
        author=data['author']
        
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

# READ all books
@app.route('/books/all', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# READ a single book by ID
@app.route('/books/<bookid>', methods=['GET'])
def get_book(bookid):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200

# UPDATE a book by book_id
@app.route('/books/<bookid>', methods=['PUT'])
def update_book(bookid):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.json
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    
    db.session.commit()
    return jsonify(book.to_dict()), 200

# DELETE a book by book_id
@app.route('/books/<bookid>', methods=['DELETE'])
def delete_book(bookid):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200

# Run the Flask app on port 5006
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
