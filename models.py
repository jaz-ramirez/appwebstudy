from flask_sqlalchemy import SQLAlchemy
#Crea una instancia de SQLAlchemy llamada db que se utilizará para manejar la base de datos.
db = SQLAlchemy()

#Define una función setup_db que toma una aplicación Flask como argumento y la inicializa con la configuración de la base de datos.
def setup_db(app):
    db.init_app(app)

#Define un modelo de base de datos llamado User que hereda de db.Model
class User(db.Model):
    #Define una columna id de tipo entero que será la clave primaria de la tabla User.
    id = db.Column(db.Integer, primary_key=True)
    #Define una columna username de tipo cadena con un máximo de 80 caracteres.
    username = db.Column(db.String(80), unique=True, nullable=False)
    #Define una columna password de tipo cadena con un máximo de 80 caracteres que no puede ser nula.
    password = db.Column(db.String(80), nullable=False)
    #Define una relación uno a muchos con el modelo FlashCard
    flashcards = db.relationship('FlashCard', backref='user', lazy=True)
#Define un modelo de base de datos llamado FlashCard que hereda de db.Model
class FlashCard(db.Model):
    #Define una columna id de tipo entero que será la clave primaria de la tabla FlashCard.
    id = db.Column(db.Integer, primary_key=True)
    #define columna del tema de la flashcard
    topic = db.Column(db.String(120), nullable=False)
    #define columna de la pregunta de flashcard
    question = db.Column(db.Text, nullable=False)
    #define columna de la contraseña de la flashcard
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

