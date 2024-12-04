# Sistema de Mensajería

Este es un sistema de mensajería simple implementado con Flask y SQLite. El sistema permite a los usuarios gestionar contactos y enviar mensajes entre ellos.

## Características Principales

El sistema ofrece las siguientes funcionalidades:
- Gestión de contactos (listar y agregar)
- Envío de mensajes entre contactos
- Visualización de mensajes recibidos
- Validación de relaciones entre usuarios

## Requisitos Previos

Para ejecutar este proyecto necesitas tener instalado Python 3.8 o superior.

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/BlackMonkcr/ef_software.git
cd ef_software
```

2. Crea un entorno virtual e instala las dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows usar: venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

Para iniciar el servidor:
```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## API Endpoints

- GET /mensajeria/contactos?mialias=XXXX - Lista los contactos de un usuario
- POST /mensajeria/contactos/{alias} - Agrega un nuevo contacto
- POST /mensajeria/enviar - Envía un mensaje a un contacto
- GET /mensajeria/recibidos?mialias=XXXX - Muestra mensajes recibidos

## Pruebas

Para ejecutar las pruebas unitarias:
```bash
python -m unittest test.py
```

Para ejecutar las pruebas con cobertura:
```bash
python -m coverage run -m unittest test.py
python -m coverage report
```

## Estructura del Proyecto

```
ef_software/
├── app.py             # Aplicación principal
├── test.py           # Pruebas unitarias
├── requirements.txt   # Dependencias
└── README.md         # Este archivo
```


## Integrantes
- Aaron Cesar Aldair Navarro Mendoza
- Gianpier André Segovia Ureta
