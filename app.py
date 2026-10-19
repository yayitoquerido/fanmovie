from flask import Flask, request, jsonify, send_file
import os
import random
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from processor import generate_lost_tape, generate_aftermovie # Comentado hasta fase de video

app = Flask(__name__, static_folder='static')

# Configuración de la Base de Datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'db'), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db', 'fanmovie.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos
db = SQLAlchemy(app)

# ==========================================
# DEFINICIÓN DE TABLAS (MODELOS RELACIONALES)
# ==========================================

class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    safe_name = db.Column(db.String(100), unique=True, nullable=False)
    fecha = db.Column(db.String(20))
    circuito = db.Column(db.String(20))
    has_banner = db.Column(db.Boolean, default=False)
    estado = db.Column(db.String(20), default='activo') # activo, editandose, publicado
    pin_admin = db.Column(db.String(10), nullable=False)
    
    # Relación: un evento tiene muchos crudos
    crudos = db.relationship('Crudo', backref='evento', lazy=True)

class Filmmaker(db.Model):
    __tablename__ = 'filmmakers'
    id = db.Column(db.Integer, primary_key=True)
    instagram = db.Column(db.String(50), unique=True, nullable=False)
    puntos = db.Column(db.Integer, default=0)
    
    # Relación: un filmmaker sube muchos crudos
    crudos = db.relationship('Crudo', backref='autor', lazy=True)

class Crudo(db.Model):
    __tablename__ = 'crudos'
    id = db.Column(db.Integer, primary_key=True)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    seleccionado = db.Column(db.Boolean, default=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Claves foráneas (relaciones)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    filmmaker_id = db.Column(db.Integer, db.ForeignKey('filmmakers.id'), nullable=False)

# Crear las tablas si no existen en el archivo SQLite
with app.app_context():
    db.create_all()

# ==========================================
# RUTAS DE LA API
# ==========================================

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    if request.method == 'GET':
        eventos = Evento.query.all()
        # Formatear la lista para enviarla al Frontend
        eventos_list = [{
            "id": e.id,
            "name": e.nombre,
            "safe_name": e.safe_name,
            "date": e.fecha,
            "circuit": e.circuito,
            "has_banner": e.has_banner,
            "status": e.estado
        } for e in eventos]
        return jsonify({"events": eventos_list})
    
    if request.method == 'POST':
        data = request.json
        safe_name = data['name'].lower().replace(' ', '_').replace('/', '')
        
        # Verificar si ya existe para no duplicar
        existe = Evento.query.filter_by(safe_name=safe_name).first()
        if existe:
            return jsonify({"status": "error", "message": "El evento ya existe"}), 400
            
        pin = str(random.randint(1000, 9999))
        
        nuevo_evento = Evento(
            nombre=data['name'],
            safe_name=safe_name,
            fecha=data['date'],
            circuito=data['circuit'],
            has_banner=data.get('has_banner', False),
            pin_admin=pin
        )
        
        db.session.add(nuevo_evento)
        db.session.commit()
        
        os.makedirs(f"uploads/{safe_name}", exist_ok=True)
        
        return jsonify({"status": "success", "event": {"name": nuevo_evento.nombre, "safe_name": nuevo_evento.safe_name}, "pin": pin})

@app.route('/api/studio/verify', methods=['POST'])
def verify_pin():
    data = request.json
    pin = data.get('pin')
    
    if pin == "2026":
        return jsonify({"status": "success", "message": "Master PIN ok"})
        
    evento = Evento.query.filter_by(pin_admin=pin).first()
    if evento:
        return jsonify({"status": "success", "event": evento.safe_name})
        
    return jsonify({"status": "error", "message": "PIN incorrecto"}), 403

if __name__ == '__main__':
    app.run(debug=True, port=5000)
