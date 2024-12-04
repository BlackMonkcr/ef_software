import unittest
import sqlite3
import os
from app import app

class TestMensajeria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.app = app.test_client()
        
        cls.conn = sqlite3.connect('mensajeria_test.db')
        cls.conn.row_factory = sqlite3.Row
        
        # Crear las tablas
        cls.conn.executescript('''
            CREATE TABLE IF NOT EXISTS usuarios (
                alias TEXT PRIMARY KEY,
                nombre TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS contactos (
                usuario_alias TEXT,
                contacto_alias TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_alias) REFERENCES usuarios (alias),
                FOREIGN KEY (contacto_alias) REFERENCES usuarios (alias),
                PRIMARY KEY (usuario_alias, contacto_alias)
            );
            
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente_alias TEXT,
                destinatario_alias TEXT,
                contenido TEXT NOT NULL,
                fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (remitente_alias) REFERENCES usuarios (alias),
                FOREIGN KEY (destinatario_alias) REFERENCES usuarios (alias)
            );
        ''')
        
        # Insertar datos de prueba
        cls.conn.executescript('''
            INSERT INTO usuarios (alias, nombre) VALUES 
                ('cpaz', 'Christian'),
                ('lmunoz', 'Luisa'),
                ('mgrau', 'Miguel');
                
            INSERT INTO contactos (usuario_alias, contacto_alias) VALUES 
                ('cpaz', 'lmunoz'),
                ('cpaz', 'mgrau'),
                ('lmunoz', 'mgrau'),
                ('mgrau', 'cpaz');
        ''')
        cls.conn.commit()

    def setUp(self):
        """Restablecer la base de datos antes de cada test"""
        # Limpiar todas las tablas
        self.conn.executescript('''
            DELETE FROM mensajes;
            DELETE FROM contactos;
            DELETE FROM usuarios;
        ''')
        
        # Reinsertar los datos de prueba
        self.conn.executescript('''
            INSERT INTO usuarios (alias, nombre) VALUES 
                ('cpaz', 'Christian'),
                ('lmunoz', 'Luisa'),
                ('mgrau', 'Miguel');
                
            INSERT INTO contactos (usuario_alias, contacto_alias) VALUES 
                ('cpaz', 'lmunoz'),
                ('cpaz', 'mgrau'),
                ('lmunoz', 'mgrau'),
                ('mgrau', 'cpaz');
        ''')
        self.conn.commit()

    def tearDown(self):
        """Limpiar después de cada test"""
        pass

    @classmethod
    def tearDownClass(cls):
        # Eliminar todas las tablas
        cls.conn.executescript('''
            DROP TABLE IF EXISTS mensajes;
            DROP TABLE IF EXISTS contactos;
            DROP TABLE IF EXISTS usuarios;
        ''')
        cls.conn.close()
        # Eliminar el archivo de la base de datos
        if os.path.exists('mensajeria_test.db'):
            os.remove('mensajeria_test.db')

    def test_obtener_contactos_exitoso(self):
        """Verifica la obtención exitosa de contactos de un usuario"""
        response = self.app.get('/mensajeria/contactos?mialias=cpaz')
        self.assertEqual(response.status_code, 200)
        expected_response = "lmunoz: Luisa\nmgrau: Miguel"
        self.assertEqual(response.data.decode().strip(), expected_response)

    def test_obtener_contactos_usuario_no_existe(self):
        """Verifica el comportamiento cuando el usuario no existe"""
        response = self.app.get('/mensajeria/contactos?mialias=noexiste')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode().strip(), "")

    def test_obtener_contactos_sin_mialias(self):
        """Verifica el error cuando no se proporciona el parámetro mialias"""
        response = self.app.get('/mensajeria/contactos')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error: Se requiere el parámetro mialias", response.data.decode())

    def test_agregar_contacto_exitoso(self):
        """Verifica la adición exitosa de un nuevo contacto"""
        response = self.app.post('/mensajeria/contactos/cpaz', 
            json={
                "contacto": "nuevo",
                "nombre": "Usuario Nuevo"
            })
        self.assertEqual(response.status_code, 200)

    def test_agregar_contacto_sin_datos(self):
        """Verifica el error al agregar contacto sin datos requeridos"""
        response = self.app.post('/mensajeria/contactos/cpaz', 
            json={})
        self.assertEqual(response.status_code, 400)

    def test_enviar_mensaje_exitoso(self):
        """Verifica el envío exitoso de un mensaje"""
        response = self.app.post('/mensajeria/enviar', 
            json={
                "usuario": "cpaz",
                "contacto": "lmunoz",
                "mensaje": "Hola, ¿cómo estás?"
            })
        self.assertEqual(response.status_code, 200)

    def test_enviar_mensaje_contacto_no_permitido(self):
        """Verifica el error al enviar mensaje a un contacto no permitido"""
        response = self.app.post('/mensajeria/enviar', 
            json={
                "usuario": "cpaz",
                "contacto": "noexiste",
                "mensaje": "hola"
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("no está en tu lista de contactos", response.data.decode())

    def test_enviar_mensaje_peticion_invalida(self):
        """Verifica el error con una petición mal formada"""
        response = self.app.post('/mensajeria/enviar', 
            json={
                "usuario": "cpaz"
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error: Faltan campos requeridos", response.data.decode())

    def test_obtener_mensajes_recibidos_exitoso(self):
        """Verifica la obtención exitosa de mensajes recibidos"""
        # Primero enviamos un mensaje
        self.app.post('/mensajeria/enviar', 
            json={
                "usuario": "cpaz",
                "contacto": "lmunoz",
                "mensaje": "Hola Luisa"
            })
        
        # Luego verificamos que se puede recuperar
        response = self.app.get('/mensajeria/recibidos?mialias=lmunoz')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Christian te escribió", response.data.decode())

    def test_obtener_mensajes_recibidos_sin_mialias(self):
        """Verifica el error al obtener mensajes sin proporcionar mialias"""
        response = self.app.get('/mensajeria/recibidos')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error: Se requiere el parámetro mialias", response.data.decode())

if __name__ == '__main__':
    unittest.main()