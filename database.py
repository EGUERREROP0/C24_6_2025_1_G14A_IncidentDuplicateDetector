# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv
# import os

# # Cargar variables del archivo .env
# load_dotenv()

# # Obtener la cadena de conexión
# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise ValueError("❌ No se encontró DATABASE_URL en el archivo .env")

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Obtener la cadena de conexión
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ No se encontró DATABASE_URL en el archivo .env")

# Crear el motor con opciones para producción
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Reconectar si la conexión se cae
    pool_size=5,             # Tamaño del pool de conexiones
    max_overflow=10,         # Conexiones adicionales si el pool se llena
     pool_recycle=1800,      # Reciclar conexiones cada 30 minutos
    connect_args={
        "sslmode": "require"  # Obligatorio para Neon
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



