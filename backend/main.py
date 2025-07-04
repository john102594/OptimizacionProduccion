"""
Este módulo contiene la aplicación FastAPI para el optimizador de producción.
Proporciona endpoints para cargar archivos Excel, procesarlos y aplicar
algoritmos de optimización (codicioso y genético) para generar cronogramas de producción.
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

# Importa las funciones de optimización desde los módulos separados
from .optimizers.greedy_optimizer import optimize_greedy
from .optimizers.genetic_optimizer3 import optimize_genetic

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

@app.get("/", summary="Endpoint de prueba", response_description="Mensaje de bienvenida a la API.")
def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "Welcome to the Production Optimizer API"}

@app.post("/upload/", summary="Optimizar cronograma con algoritmo codicioso",
          response_description="Cronograma optimizado y resumen original por máquina.")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Procesa un archivo Excel cargado y genera un cronograma de producción optimizado
    utilizando un algoritmo codicioso.

    Args:
        file (UploadFile): El archivo Excel a cargar.

    Returns:
        dict: Un diccionario que contiene el cronograma optimizado por máquina
              y un resumen original de referencias y metros por máquina.
              En caso de error, devuelve un diccionario con un mensaje de error.
    """
    contents = await file.read()
    try:
        # Lee el archivo Excel en un DataFrame de Pandas
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')

        # Normaliza los nombres de las columnas: convierte a minúsculas y reemplaza espacios por guiones bajos.
        # Se asume que el archivo Excel contiene las siguientes columnas (ejemplos):
        # - 'Maquina Sugerida' -> 'maquina_sugerida' (str)
        # - 'Metros Requeridos' -> 'metros_requeridos' (float)
        # - 'Velocidad Sugerida' -> 'velocidad_sugerida' (float)
        # - 'Nivel de Criticidad' -> 'nivel_de_criticidad' (int)
        # - 'Tipo de Impresion' -> 'tipo_de_impresion' (str)
        # - 'Diametro de Manga' -> 'diametro_de_manga' (float)
        # - 'Referencia' -> 'referencia' (str)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Calcula el resumen original de referencias y metros por cada máquina
        # Este resumen se basa en los datos del Excel original, antes de la optimización.
        original_summary_per_machine = {}
        for machine in df['maquina_sugerida'].unique():
            machine_df = df[df['maquina_sugerida'] == machine]
            original_summary_per_machine[machine] = {
                "num_references": int(len(machine_df)),  # Número de referencias para esta máquina
                "total_meters": float(machine_df['metros_requeridos'].sum())  # Total de metros para esta máquina
            }

        # Llama a la función de optimización codiciosa
        optimized_schedule = optimize_greedy(df)

        # Devuelve el cronograma optimizado y el resumen original
        return {
            "optimized_schedule": optimized_schedule,
            "original_summary": original_summary_per_machine
        }
    except Exception as e:
        # Captura cualquier excepción durante el procesamiento y devuelve un mensaje de error
        return {"error": str(e)}

@app.post("/upload-ga/", summary="Optimizar cronograma con algoritmo genético",
          response_description="Cronograma optimizado y resumen original por máquina.")
async def create_upload_file_ga(file: UploadFile = File(...)):
    """
    Procesa un archivo Excel cargado y genera un cronograma de producción optimizado
    utilizando un algoritmo genético.

    Args:
        file (UploadFile): El archivo Excel a cargar.

    Returns:
        dict: Un diccionario que contiene el cronograma optimizado por máquina
              y un resumen original de referencias y metros por máquina.
              En caso de error, devuelve un diccionario con un mensaje de error.
    """
    contents = await file.read()
    try:
        # Lee el archivo Excel en un DataFrame de Pandas
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        
        # Normaliza los nombres de las columnas (ver comentarios en /upload/ para detalles)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Calcula el resumen original de referencias y metros por cada máquina
        original_summary_per_machine = {}
        for machine in df['maquina_sugerida'].unique():
            machine_df = df[df['maquina_sugerida'] == machine]
            original_summary_per_machine[machine] = {
                "num_references": int(len(machine_df)),
                "total_meters": float(machine_df['metros_requeridos'].sum())
            }

        # Llama a la función de optimización genética
        optimized_schedule_ga = optimize_genetic(df)

        # Formatea el cronograma optimizado para la respuesta JSON
        # Asegura que los tipos de datos sean compatibles con JSON (ej. float en lugar de numpy.float64)
        schedule_per_machine_formatted = {}
        for machine, schedule_list in optimized_schedule_ga.items():
            schedule_per_machine_formatted[machine] = []
            for job in schedule_list:
                schedule_per_machine_formatted[machine].append({
                    'orden': job['orden'],
                    'referencia': job['referencia'],
                    'tipo_de_impresion': job['tipo_de_impresion'],
                    'diametro_de_manga': float(job['diametro_de_manga']),
                    'metros_requeridos': float(job['metros_requeridos']),
                    'velocidad_sugerida_m_min': float(job['velocidad_sugerida_m_min']),
                    'tiempo_estimado_horas': float(job['tiempo_estimado_horas']),
                    'tiempo_de_cambio_horas': float(job['tiempo_de_cambio_horas']),
                    'hora_inicio': float(job['hora_inicio']),
                    'hora_fin': float(job['hora_fin'])
                })

        # Devuelve el cronograma optimizado y el resumen original
        return {
            "optimized_schedule": schedule_per_machine_formatted,
            "original_summary": original_summary_per_machine
        }
    except Exception as e:
        # Captura cualquier excepción durante el procesamiento y devuelve un mensaje de error
        return {"error": str(e)}
