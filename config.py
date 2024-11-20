import os
#devuelve la ruta absoluta del directorio donde se encuentra el archivo actual.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    #SECRET_KEY se obtiene de las variables de entorno con os.getenv('SECRET_KEY', 'default_secret_key'). Si no se encuentra una variable de entorno llamada SECRET_KEY, se utiliza 'default_secret_key' como valor predeterminado.
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    #SQLALCHEMY_DATABASE_URI define la URI de conexión para SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flashcards.db')
    #Desactivar seguimiento de modificaciones de SQLAlchemy:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
