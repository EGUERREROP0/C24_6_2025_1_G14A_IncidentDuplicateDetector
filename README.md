# -*- coding: utf-8 -*-
# Evitar Duplicados en Base de Datos
# Este proyecto es una API RESTful que permite evitar la creación de registros duplicados en una base de datos PostgreSQL.
# Requisitos

git clone https://github.com/usuario/evitarduplicados.git
cd evitarduplicados
# Si ya tienes tu entorno virtual creado, puedes omitir este paso.
venv\Scripts\activate


# Crear un entorno virtual si no tines
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate


pip install -r requirements.txt
# Configuración de la Base de Datos

DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/tu_basededatos
uvicorn main:app --reload
http://localhost:8000/docs
