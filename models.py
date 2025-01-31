from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    
    # Relación de un usuario a muchas películas
    peliculas = db.relationship('Pelicula', backref='usuario', lazy=True)

# Modelo de Pelicula
class Pelicula(db.Model):
    id_pelicula = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(50), nullable=False)
    fecha_estreno = db.Column(db.String(15), unique=True, nullable=False)
    sinopsis = db.Column(db.Text, nullable=False)
    
    # Clave foránea hacia el usuario
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.String(15), unique=True, nullable=False)
    
    # Clave foránea hacia el usuario
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Clave foránea hacia la película
    id_pelicula = db.Column(db.Integer, db.ForeignKey('pelicula.id_pelicula'), nullable=False)
    
    usuario = db.relationship('Usuario', backref='comentarios', lazy=True)
    pelicula = db.relationship('Pelicula', backref='comentarios', lazy=True)

