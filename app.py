#render template sabe que los html están en templates, por lo que en la ruta a los archivos html ya no es necesario poner el nombre de la carpeta
#reqiest es la solicitud que se hace
#
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import openai 
import os
from models import db, setup_db, User, FlashCard
import re



# Importar modelos
def create_app():
    load_dotenv() #Carga el archivo .env para usar la variable OPENAI_API_KEY.
    # Configuración de la API de OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    # Configurar la clave de API de OpenAI
    openai.api_key = api_key


    app = Flask(__name__) #Crea la instancia principal de Flask.
    app.config['SECRET_KEY'] = 'final' #Clave utilizada para firmar datos importantes (como la sesión del usuario).
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db' #Configuración para conectar la aplicación a una base de datos SQLite.
    setup_db(app) #Inicializa la configuración de SQLAlchemy desde el módulo models.



    # *************************      Rutas y Vistas     ***********************
    #ruta a la página de inicio
    @app.route('/')
    def index():
        #Carga la página de inicio de sesión desde el archivo login.html.
        return render_template('login.html') 
    
    #Página principal
    @app.route('/home', methods=['GET','POST'])
    def home():
        if 'user_id' not in session: #Verifica si el usuario está autenticado
            return redirect(url_for('login'))
        user_id=session['user_id']
        # Consultar el usuario usando el user_id
        user = get_user_by_id(user_id)  # Asume que devuelve un diccionario con los datos del usuario
        username = user.get('username', 'Usuario')  # Obtiene el 'username' o usa 'Usuario' como predeterminado
        #Renderiza la página home.html, mostrando el nombre del usuario.
        return render_template('home.html', username=username)
    #Función para obtener el ususario
    def get_user_by_id(user_id):
        # Consulta en la base de datos un usuario por su id.
        user = User.query.filter_by(id=user_id).first()
        #Devuelve un diccionario con el nombre de usuario, o uno vacío si no existe.
        return {'username': user.username} if user else {}


    #Pàgina crear tarjeta 
    @app.route('/create', methods=['GET', 'POST'])
    def create_card():
        #Recibe datos del usuario mediante un formulario POST.
        if request.method == 'POST':
            chat_history = [] #crea un arreglo para guardar info
            topic = request.form['topic'] #toma el tema
            content = request.form['content'] #toma el contenido
            # Instrucciones para el modelo
            #se le indica que es un asitente 
            system_message = { 
                "role": "system",
                "content": "Eres un asistente creador de flashcards. Por favor, realiza flashcards correctas"
            }
            chat_history.append(system_message) #se agrega al arreglo
            #se le pasa el tema principal de las flashcards
            main_topic = { 
                "role": "user",
                "content": f"El tema principal es {topic}"
            }
            chat_history.append(main_topic)
            #se le instruye sobre qué tema específico deberían ser las flashcards y el formato en el que las tiene que geenrar
            about = {
                "role": "user",
                "content": f"Genera flashcards sobre {content} en el formato 'Pregunta: ... Respuesta: ...' para cada flashcard, no agregues nada más de texto."
            }

            chat_history.append(about)
            #Se maneja el error por si la api no funciona
            try:
                #Usa la API de OpenAI para generar texto basado en el tema y contenido proporcionados.
                response = openai.chat.completions.create(
                    messages= chat_history,
                    model="gpt-4o-mini", #version utilizada
                    
                )
                generated_content = response.choices[0].message.content.strip()
                  # Parsear las preguntas y respuestas
                flashcards = parse_flashcards(generated_content)

                #Guarda las flashcards en la base de datos.
                for flashcard in flashcards:
                    #se intancia un nuevo objeto de las flash cards
                    new_card = FlashCard(topic=topic, question=flashcard['question'], answer=flashcard['answer'], user_id=session['user_id'])
                    db.session.add(new_card)
                #se guardan los cambios
                db.session.commit()
                return redirect(url_for('topics')) #se redirecciona a la página donde se encuentran los temas principales.
            except Exception as e: #si no se puede crear la flascard se manda el error
                return f"Error al generar la flashcard: {e}" #se muetra el error generado
        return render_template('create_card.html') #renderizado para la creación de tarjetas
    
    #Para pasar de texto a un diccionario que contenga las preguntas y respuestas
    def parse_flashcards(generated_content):
        flashcards = []
            # Utilizamos una expresión regular para encontrar todas las "Pregunta" y "Respuesta"
        matches = re.findall(r"Pregunta:\s*(.*?)\s*Respuesta:\s*(.*?)(?=\nPregunta:|$)", generated_content, re.DOTALL)
        
        # Cada "match" es un par (pregunta, respuesta)
        for question, answer in matches:
            flashcards.append({ #se agregan a un arreglo que contendrá la información de las flashcard
                "question": question.strip(),
                "answer": answer.strip()
            })
        print(flashcards)
        return flashcards
    #vista de temas de las flashcards
    @app.route('/topics')
    def topics():
        #obtiene el id del usuario 
        user_id = session.get('user_id')
        # Obtener todos los temas únicos de las flashcards del usuario
        topics = db.session.query(FlashCard.topic).filter_by(user_id=user_id).distinct().all()
        return render_template('topics.html', topics=[t[0] for t in topics])

    
    #página de las flashcards de acuerdo al tema elegido
    @app.route('/history/<topic>')
    def history(topic):
        #obtiene el id del usuario
        user_id = session.get('user_id')
        # Filtrar las flashcards por usuario y tema
        flashcards = FlashCard.query.filter_by(user_id=user_id, topic=topic).all()
        return render_template('history.html', topic=topic, flashcards=flashcards)

    #página de inicio de sesión 
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        #toma los datos ingresados por el usuario en el formulario 
        if request.method == 'POST': 
                username=request.form['username'] #ususario
                password=request.form['password'] #contraseña
                user = User.query.filter_by(username=username,
                                            password=password).first()
                #Si las credenciales son correctas, se guarda el user_id en la sesión y se redirige al muro. Si no, se muestra un mensaje de error.
                if user: #si coincidió el usuario con su contraseña, es true
                    session['user_id']=user.id
                    return redirect(url_for('home')) #se redirige al muro
                else: #si no es true, entonces se le señala al usuario
                    flash('Login fallido. Por favor verifica tus credenciales',
                        'error') #mensaje de error
                    return redirect(url_for('index'))
    #funcionalidad para cerrar sesión               
    @app.route('/logout')
    def logout():
        session.clear() #cierra sesión
        return redirect(url_for('index')) #redirige a la página de iniciode sesión          

    #página de registro de nuevo usuario
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        #toma los datos ingresados en el formulario por medio del mètodo post
        if request.method == 'POST':
            username = request.form['username']
            password=request.form['password']
            #hace una nueva instancia del objeto usuario
            new_user = User(username=username,
                            password=password)
            #agrega el nuevo usuario creado a la base de datos
            db.session.add(new_user)
            db.session.commit() #guarda los cambios realizados
            session['user_id'] = new_user.id
            return redirect(url_for('index')) #redirige a la página de inicio de sesión
        return render_template('register.html') # Renderizar el formulario de registro
    return app
#función principal del programa
if __name__ == '__main__':
    app=create_app() #se crea la aplicación web
    with app.app_context():
        db.create_all() #crea la base de datos
    app.run(debug=True, port=5001) #debug para que se muestren los cambios directamente en la pàgina web 


