from flask import Flask, render_template, request, url_for, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

from models import db, Usuario, Pelicula, Comentario

app = Flask(__name__)
app.secret_key = '@Admin123'

# Configuración de la base de datos MySQL usando la variable de entorno MYSQL_URL
app .config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:fhHvCmIamLdjUwmzlnROdjIiICYbiGBW@junction.proxy.rlwy.net:23095/railway"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()  # Limpia todos los datos de la sesión
    flash('Has cerrado sesión exitosamente.', 'success')  # Mensaje de éxito
    return redirect(url_for('home'))  # Redirige a la página principal o de login

# Ruta para el registro de usuario
@app.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    contrasena = request.form['contrasena']
    confirmar_contrasena = request.form['confirmar_contrasena']
    
    # Validaciones
    if Usuario.query.filter_by(email=email).first():
        flash('El email ya está registrado.', 'danger')
    elif contrasena != confirmar_contrasena:
        flash('Las contraseñas no coinciden.', 'danger')
    else:
        hash_password = generate_password_hash(contrasena)
        new_user = Usuario(nombre=nombre, apellido=apellido, email=email, contrasena=hash_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso, ahora puede iniciar sesión.', 'success')
        return redirect(url_for('home'))
    
    return redirect(url_for('home'))

# Ruta para el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    contrasena = request.form['contrasena']
    usuario = Usuario.query.filter_by(email=email).first()
    
    if usuario and check_password_hash(usuario.contrasena, contrasena):
        flash('Inicio de sesión exitoso.', 'success')
        
        # ID, nombre y apellido del usuario en la sesión
        session['usuario'] = {'id': usuario.id, 'nombre': usuario.nombre, 'apellido': usuario.apellido}
        
        return redirect(url_for('cine'))  # Redirige a la vista de películas
    else:
        flash('Credenciales incorrectas.', 'danger')
        return redirect(url_for('home'))  # Vuelve al login en caso de error

@app.route('/cine')
def cine():
    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:  
        flash('Por favor, inicia sesión para ver la lista de películas.', 'warning')
        return redirect(url_for('home'))  # Redirige a la página de home si no está autenticado
    
    # Obtener todas las películas
    peliculas = Pelicula.query.all()
    usuario = session.get('usuario')
    return render_template('cine.html', peliculas=peliculas, usuario=usuario)

@app.route('/crear-pelicula', methods=['GET', 'POST'])
def crear_pelicula():
    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:  
        flash('Por favor, inicia sesión para crear una película.', 'warning')
        return redirect(url_for('home'))  
    
    print("Sesión actual:", session)

    if request.method == 'POST':
        # Obtener los datos del formulario
        titulo = request.form['titulo']
        director = request.form['director']
        fecha_estreno = request.form['fecha_estreno']
        sinopsis = request.form['sinopsis']

        # Verificar si ya existe una película con ese título
        if Pelicula.query.filter_by(titulo=titulo).first():
            flash('Ya existe una película con ese título.', 'danger')
            return render_template('nueva_pelicula.html', sinopsis=sinopsis)

        # Obtener el ID del usuario desde la sesión
        id_usuario = session['usuario']['id']  #  ID del usuario desde la sesión
        print("ID del usuario:", id_usuario)

        nueva_pelicula = Pelicula(titulo=titulo, director=director, fecha_estreno=fecha_estreno, sinopsis=sinopsis, id_usuario=id_usuario)
        db.session.add(nueva_pelicula)
        db.session.commit()
        
        # Mensaje de éxito y redirigir al listado de películas
        flash('Película creada correctamente.', 'success')
        return redirect(url_for('cine'))  
    
    return render_template('nueva_pelicula.html')  # Muestra el formulario

@app.route('/cine/<int:id>', methods=['GET', 'POST'])
def ver_pelicula(id):
    pelicula = Pelicula.query.get_or_404(id)
    usuario = Usuario.query.get_or_404(pelicula.id_usuario)
    comentarios = Comentario.query.filter_by(id_pelicula=id).order_by(Comentario.fecha.desc()).all()

    # Verificar si el usuario ha iniciado sesión y permitir comentarios
    if 'usuario' in session:
        # Si el usuario no es el dueño de la película, permite comentar
        if session['usuario']['id'] != pelicula.id_usuario:
            if request.method == 'POST':
                contenido = request.form['contenido']
                fecha = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')

                # Crear y guardar el comentario
                comentario = Comentario(contenido=contenido, fecha=fecha, id_usuario=session['usuario']['id'], id_pelicula=id)
                db.session.add(comentario)
                db.session.commit()
                
                flash('Comentario publicado con éxito.', 'success')
                return redirect(url_for('ver_pelicula', id=id))

        else:
            flash('No puedes comentar en tu propia película.', 'warning')

    return render_template('ver_pelicula.html', pelicula=pelicula, usuario=usuario, comentarios=comentarios)

@app.route('/pelicula/editar/<int:id>', methods=['GET', 'POST'])
def editar_pelicula(id):
    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:  
        flash('Por favor, inicia sesión para editar una película.', 'warning')
        return redirect(url_for('home'))  
    
    pelicula = Pelicula.query.get_or_404(id)  # Busca la película o devuelve 404 si no existe
    if request.method == 'POST':
        # Obtener el nuevo título
        nuevo_titulo = request.form['titulo']
        
        # Verificar si ya existe una película con ese título, excluyendo la actual
        if Pelicula.query.filter(Pelicula.titulo == nuevo_titulo, Pelicula.id_pelicula != id).first():
            flash('Ya existe una película con ese título.', 'danger')
            return render_template('nueva_pelicula.html', pelicula=pelicula, editar=True)

        # Actualiza los datos de la película
        pelicula.titulo = nuevo_titulo
        pelicula.director = request.form['director']
        pelicula.fecha_estreno = request.form['fecha_estreno']
        pelicula.sinopsis = request.form['sinopsis']
        db.session.commit()
        flash('Película actualizada correctamente.', 'success')
        return redirect(url_for('cine'))
    
    return render_template('nueva_pelicula.html', pelicula=pelicula, editar=True)

@app.route('/pelicula/borrar/<int:id>', methods=['POST'])
def borrar_pelicula(id):
    pelicula = Pelicula.query.get_or_404(id)  # Busca la película o devuelve 404 si no existe
    db.session.delete(pelicula)
    db.session.commit()
    flash('Película borrada correctamente.', 'success')
    return redirect(url_for('cine'))  # Redirige al listado de películas

@app.route('/eliminar_comentario/<int:comentario_id>', methods=['POST'])
def eliminar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)

    # Verificar que el usuario que intenta eliminar el comentario es el autor
    if 'usuario' in session and session['usuario']['id'] == comentario.id_usuario:
        db.session.delete(comentario)
        db.session.commit()
        flash('Comentario eliminado con éxito.', 'success')
    else:
        flash('No tienes permiso para eliminar este comentario.', 'danger')

    return redirect(url_for('ver_pelicula', id=comentario.id_pelicula))


@app.route('/test-db')
def test_db():
    try:
        db.engine.connect()
        return "¡Conexión a la base de datos exitosa!"
    except Exception as e:
        return f"Error al conectar a la base de datos: {str(e)}"
  

if __name__ == '__main__':
    app.run(debug=True)
