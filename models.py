from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_db(app):
    db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    flashcards = db.relationship('FlashCard', backref='user', lazy=True)

class FlashCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

