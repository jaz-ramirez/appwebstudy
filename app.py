#render template sabe que los html están en templates, por lo que en la ruta a los archivos html ya no es necesario poner el nombre de la carpeta
#reqiest es la solicitud que se hace
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import openai 
import os
from models import db, setup_db, User, FlashCard
import re



# Importar modelos
def create_app():
    load_dotenv()
    # Configuración de la API de OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    # Configurar la clave de API de OpenAI
    openai.api_key = api_key


    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'final'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
    setup_db(app)



    # Rutas y Vistas
    @app.route('/')
    def index():
        return render_template('login.html') #ruta a la página principal del sitio web

    @app.route('/home', methods=['GET','POST'])
    def home():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user_id=session['user_id']

        return render_template('home.html')

    @app.route('/create', methods=['GET', 'POST'])
    def create_card():
        if request.method == 'POST':
            chat_history = []
            topic = request.form['topic']
            content = request.form['content']
                # Instrucciones para el modelo
            system_message = {
                "role": "system",
                "content": "Eres un asistente creador de flashcards. Por favor, realiza flashcards correctas"
            }
            chat_history.append(system_message)
            main_topic = {
                "role": "user",
                "content": f"El tema principal es {topic}"
            }
            chat_history.append(main_topic)
            about = {
                "role": "user",
                "content": f"Genera flashcards sobre {content} en el formato 'Pregunta: ... Respuesta: ...' para cada flashcard, no agregues nada más de texto."
            }

            chat_history.append(about)
            try:
                response = openai.chat.completions.create(
                    messages= chat_history,
                    model="gpt-4o-mini",
                    
                )
                generated_content = response.choices[0].message.content.strip()
                  # Parsear las preguntas y respuestas
                flashcards = parse_flashcards(generated_content)

                #print(generated_content)
                for flashcard in flashcards:
                    new_card = FlashCard(topic=topic, question=flashcard['question'], answer=flashcard['answer'], user_id=session['user_id'])
                    db.session.add(new_card)
                db.session.commit()
                return redirect(url_for('topics'))
            except Exception as e:
                return f"Error al generar la flashcard: {e}"
        return render_template('create_card.html')
    

    def parse_flashcards(generated_content):
        flashcards = []
            # Utilizamos una expresión regular para encontrar todas las "Pregunta" y "Respuesta"
        matches = re.findall(r"Pregunta:\s*(.*?)\s*Respuesta:\s*(.*?)(?=\nPregunta:|$)", generated_content, re.DOTALL)
        
        # Cada "match" es un par (pregunta, respuesta)
        for question, answer in matches:
            flashcards.append({
                "question": question.strip(),
                "answer": answer.strip()
            })
        print(flashcards)
        return flashcards

    @app.route('/topics')
    def topics():
        user_id = session.get('user_id')
        # Obtener todos los temas únicos de las flashcards del usuario
        topics = db.session.query(FlashCard.topic).filter_by(user_id=user_id).distinct().all()
        return render_template('topics.html', topics=[t[0] for t in topics])

    

    @app.route('/history/<topic>')
    def history(topic):
        user_id = session.get('user_id')
        # Filtrar las flashcards por usuario y tema
        flashcards = FlashCard.query.filter_by(user_id=user_id, topic=topic).all()
        return render_template('history.html', topic=topic, flashcards=flashcards)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
                username=request.form['username']
                password=request.form['password']
                user = User.query.filter_by(username=username,
                                            password=password).first()
                #Si las credenciales son correctas, se guarda el user_id en la sesión y se redirige al muro. Si no, se muestra un mensaje de error.
                if user: #si coincidió el usuario con su contraseña, es true
                    session['user_id']=user.id
                    return redirect(url_for('home')) #se redirige al muro
                else: #si no es tru
                    flash('Login fallido. Por favor verifica tus credenciales',
                        'error') #mensaje de error
                    return redirect(url_for('index'))
                
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))            

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password=request.form['password']
            new_user = User(username=username,
                            password=password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('index'))
        return render_template('register.html')
    return app
if __name__ == '__main__':
    app=create_app()
    with app.app_context():
        db.create_all() #
    app.run(debug=True, port=5001) #debug para que se muestren los cambios directamente en la pàgina web 


#puntos a implementar:
'''
*Url dinámicas
*error para cuando se meta a páginas no existentes en el sistema, redireccionando a index u otra
'''