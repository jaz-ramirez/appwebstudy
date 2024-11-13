import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flashcards.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
