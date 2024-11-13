from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import openai
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
db = SQLAlchemy(app)

# Configuración de la API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Importar modelos
from models import User, FlashCard

# Rutas y Vistas
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create', methods=['GET', 'POST'])
def create_card():
    if request.method == 'POST':
        topic = request.form['topic']
        content = request.form['content']
        # Aquí llamamos a la API de OpenAI para generar el contenido de la flashcard
        try:
            response = openai.Completion.create(
                engine="davinci",
                prompt=f"Create a flashcard about {topic}.",
                max_tokens=150
            )
            generated_content = response.choices[0].text.strip()
            new_card = FlashCard(topic=topic, content=generated_content, user_id=session['user_id'])
            db.session.add(new_card)
            db.session.commit()
            return redirect(url_for('history'))
        except Exception as e:
            return f"Error al generar la flashcard: {e}"
    return render_template('create_card.html')

@app.route('/history')
def history():
    user_id = session.get('user_id')
    flashcards = FlashCard.query.filter_by(user_id=user_id).all()
    return render_template('history.html', flashcards=flashcards)

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['user_id'] = 1  # Simula un inicio de sesión con un usuario existente
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('home'))
    return render_template('register.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
