from models import db  
from app import app  

# Crear el contexto de la aplicación
with app.app_context():
    db.create_all()  # Crea todas las tablas
    print("Base de datos y tablas creadas.")