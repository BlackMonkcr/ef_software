from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos
def get_db():
    if app.config.get('TESTING'):
        conn = sqlite3.connect('mensajeria_test.db')
    else:
        conn = sqlite3.connect('mensajeria.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicialización de la base de datos
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                alias TEXT PRIMARY KEY,
                nombre TEXT NOT NULL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contactos (
                usuario_alias TEXT,
                contacto_alias TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_alias) REFERENCES usuarios (alias),
                FOREIGN KEY (contacto_alias) REFERENCES usuarios (alias),
                PRIMARY KEY (usuario_alias, contacto_alias)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente_alias TEXT,
                destinatario_alias TEXT,
                contenido TEXT NOT NULL,
                fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (remitente_alias) REFERENCES usuarios (alias),
                FOREIGN KEY (destinatario_alias) REFERENCES usuarios (alias)
            )
        ''')

# Clase DataHandler para manejar la lógica de datos
class DataHandler:
    @staticmethod
    def get_contactos(alias):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.alias, u.nombre
                FROM usuarios u
                JOIN contactos c ON u.alias = c.contacto_alias
                WHERE c.usuario_alias = ?
                AND u.alias != ?
            ''', (alias, alias))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def agregar_contacto(usuario_alias, contacto_alias, nombre):
        with get_db() as conn:
            cursor = conn.cursor()
            # Verificar si el usuario existe, si no, crearlo
            cursor.execute('INSERT OR IGNORE INTO usuarios (alias, nombre) VALUES (?, ?)',
                         (usuario_alias, usuario_alias))
            cursor.execute('INSERT OR IGNORE INTO usuarios (alias, nombre) VALUES (?, ?)',
                         (contacto_alias, nombre))
            # Agregar la relación de contacto
            cursor.execute('''
                INSERT OR IGNORE INTO contactos (usuario_alias, contacto_alias)
                VALUES (?, ?)
            ''', (usuario_alias, contacto_alias))
            conn.commit()
            return True

    @staticmethod
    def enviar_mensaje(remitente, destinatario, contenido):
        with get_db() as conn:
            cursor = conn.cursor()
            # Verificar si el destinatario es un contacto del remitente
            cursor.execute('''
                SELECT 1 FROM contactos 
                WHERE usuario_alias = ? AND contacto_alias = ?
            ''', (remitente, destinatario))
            
            if not cursor.fetchone():
                return False, "El destinatario no está en tu lista de contactos"
            
            # Enviar el mensaje
            cursor.execute('''
                INSERT INTO mensajes (remitente_alias, destinatario_alias, contenido)
                VALUES (?, ?, ?)
            ''', (remitente, destinatario, contenido))
            conn.commit()
            return True, "Mensaje enviado exitosamente"

    @staticmethod
    def obtener_mensajes_recibidos(alias):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.id, m.remitente_alias, m.contenido, m.fecha_envio,
                       u.nombre as remitente_nombre
                FROM mensajes m
                JOIN usuarios u ON m.remitente_alias = u.alias
                WHERE m.destinatario_alias = ?
                ORDER BY m.fecha_envio DESC
            ''', (alias,))
            return [dict(row) for row in cursor.fetchall()]

# Endpoints
@app.route('/mensajeria/contactos', methods=['GET'])
def obtener_contactos():
    mi_alias = request.args.get('mialias')
    if not mi_alias:
        return "Error: Se requiere el parámetro mialias", 400
    
    contactos = DataHandler.get_contactos(mi_alias)
    # Formato texto plano
    response_text = "\n".join([f"{c['alias']}: {c['nombre']}" for c in contactos])
    return response_text

@app.route('/mensajeria/contactos/<alias>', methods=['POST'])
def agregar_contacto(alias):
    data = request.get_json()
    if not data or 'contacto' not in data or 'nombre' not in data:
        return jsonify({"error": "Se requieren los campos 'contacto' y 'nombre'"}), 400
    
    resultado = DataHandler.agregar_contacto(alias, data['contacto'], data['nombre'])
    return jsonify({"success": resultado})

@app.route('/mensajeria/enviar', methods=['POST'])
def enviar_mensaje():
    data = request.get_json()
    if not data or 'usuario' not in data or 'contacto' not in data or 'mensaje' not in data:
        return "Error: Faltan campos requeridos", 400
    
    success, message = DataHandler.enviar_mensaje(
        data['usuario'],
        data['contacto'],
        data['mensaje']
    )
    
    if not success:
        return f"Error: {message}", 400
    return message

@app.route('/mensajeria/recibidos', methods=['GET'])
def obtener_mensajes_recibidos():
    mi_alias = request.args.get('mialias')
    if not mi_alias:
        return "Error: Se requiere el parámetro mialias", 400
    
    mensajes = DataHandler.obtener_mensajes_recibidos(mi_alias)
    # Formato texto plano con el formato específico
    response_lines = []
    for mensaje in mensajes:
        fecha = datetime.strptime(mensaje['fecha_envio'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
        response_lines.append(f"{mensaje['remitente_nombre']} te escribió \"{mensaje['contenido']}\" el {fecha}.")
    
    return "\n".join(response_lines)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)