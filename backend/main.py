"""
Este módulo contiene la aplicación FastAPI para el optimizador de producción.
Proporciona endpoints para cargar archivos Excel, procesarlos y aplicar
algoritmos de optimización (codicioso y genético) para generar cronogramas de producción.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from .database import create_tables
from .routers import machine_router, sleeve_set_router, optimization_router

# Inicializa la aplicación FastAPI
app = FastAPI(
    title="Production Optimizer API",
    description="API para optimizar cronogramas de producción usando algoritmos codiciosos y genéticos.",
    version="1.0.0"
)

# Configuración del middleware CORS (Cross-Origin Resource Sharing)
# Esto permite que el frontend (que se ejecuta en un origen diferente) pueda hacer solicitudes a esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite solicitudes desde cualquier origen (para desarrollo)
    allow_credentials=True,  # Permite el uso de credenciales (cookies, encabezados de autorización)
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados HTTP
)

# Asegura que las tablas se creen al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/", summary="Endpoint de prueba", response_description="Mensaje de bienvenida a la API.")
def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "Welcome to the Production Optimizer API"}

# Incluir routers
app.include_router(machine_router)
app.include_router(sleeve_set_router)
app.include_router(optimization_router)
