"""
Este módulo contiene la aplicación FastAPI para el optimizador de producción.
Proporciona endpoints para cargar archivos Excel, procesarlos y aplicar
algoritmos de optimización (codicioso y genético) para generar cronogramas de producción.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
from typing import List, Optional
import json
import datetime
import hashlib
import numpy as np

from .database import create_tables, create_sleeve_set, get_sleeve_set, get_all_sleeve_sets, update_sleeve_set, delete_sleeve_set,     create_machine, get_machine, get_all_machines, update_machine, delete_machine,     add_machine_sleeve_set_compatibility, remove_machine_sleeve_set_compatibility,     get_compatible_sleeve_sets_for_machine, get_compatible_machines_for_sleeve_set,     create_optimization_result, create_uploaded_file_info, get_latest_optimization_result_by_algorithm

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

# Modelos Pydantic para validación de datos
class SleeveSetBase(BaseModel):
    development: int
    num_sleeves: int
    status: str # 'disponible', 'en uso', 'fuera de servicio'

class SleeveSetCreate(SleeveSetBase):
    pass

class SleeveSet(SleeveSetBase):
    id: int

    class Config:
        orm_mode = True

class MachineBase(BaseModel):
    machine_number: str
    max_material_width: float

class MachineCreate(MachineBase):
    pass

class Machine(MachineBase):
    id: int

    class Config:
        orm_mode = True

class OptimizationResult(BaseModel):
    id: int
    algorithm_type: str
    timestamp: str
    total_time: float
    total_cost: float
    schedule_details: str

    class Config:
        orm_mode = True

class UploadedFileInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: str
    file_hash: str

    class Config:
        orm_mode = True

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


# Endpoints para Sleeve Sets
@app.post("/sleeve_sets/", response_model=SleeveSet, summary="Crear un nuevo set de mangas")
def create_new_sleeve_set(sleeve_set: SleeveSetCreate):
    try:
        new_sleeve_set = create_sleeve_set(sleeve_set.development, sleeve_set.num_sleeves, sleeve_set.status)
        return new_sleeve_set
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sleeve_sets/{sleeve_set_id}", response_model=SleeveSet, summary="Obtener un set de mangas por ID")
def get_single_sleeve_set(sleeve_set_id: int):
    sleeve_set = get_sleeve_set(sleeve_set_id)
    if not sleeve_set:
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    return sleeve_set

@app.get("/sleeve_sets/", response_model=List[SleeveSet], summary="Obtener todos los sets de mangas")
def get_all_sleeve_sets_endpoint():
    return get_all_sleeve_sets()

@app.put("/sleeve_sets/{sleeve_set_id}", response_model=SleeveSet, summary="Actualizar un set de mangas existente")
def update_existing_sleeve_set(sleeve_set_id: int, sleeve_set: SleeveSetCreate):
    updated_sleeve_set = update_sleeve_set(sleeve_set_id, sleeve_set.development, sleeve_set.num_sleeves, sleeve_set.status)
    if not updated_sleeve_set:
        raise HTTPException(status_code=404, detail="Sleeve Set not found or no changes applied")
    return updated_sleeve_set

@app.delete("/sleeve_sets/{sleeve_set_id}", summary="Eliminar un set de mangas")
def delete_single_sleeve_set(sleeve_set_id: int):
    if not delete_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    return {"message": "Sleeve Set deleted successfully"}

# Endpoints para Máquinas
@app.post("/machines/", response_model=Machine, summary="Crear una nueva máquina")
def create_new_machine(machine: MachineCreate):
    try:
        new_machine = create_machine(machine.machine_number, machine.max_material_width)
        return new_machine
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/machines/{machine_id}", response_model=Machine, summary="Obtener una máquina por ID")
def get_single_machine(machine_id: int):
    machine = get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@app.get("/machines/", response_model=List[Machine], summary="Obtener todas las máquinas")
def get_all_machines_endpoint():
    return get_all_machines()

@app.put("/machines/{machine_id}", response_model=Machine, summary="Actualizar una máquina existente")
def update_existing_machine(machine_id: int, machine: MachineCreate):
    updated_machine = update_machine(machine_id, machine.machine_number, machine.max_material_width)
    if not updated_machine:
        raise HTTPException(status_code=404, detail="Machine not found or no changes applied")
    return updated_machine

@app.delete("/machines/{machine_id}", summary="Eliminar una máquina")
def delete_single_machine(machine_id: int):
    if not delete_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"message": "Machine deleted successfully"}

# Endpoints de compatibilidad entre Máquinas y Sleeve Sets
@app.post("/machines/{machine_id}/compatible_sleeve_sets/{sleeve_set_id}", summary="Asociar un set de mangas a una máquina")
def add_compatibility(machine_id: int, sleeve_set_id: int):
    if not get_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    if not get_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    if add_machine_sleeve_set_compatibility(machine_id, sleeve_set_id):
        return {"message": "Compatibility added successfully"}
    raise HTTPException(status_code=400, detail="Compatibility already exists or invalid IDs")

@app.delete("/machines/{machine_id}/compatible_sleeve_sets/{sleeve_set_id}", summary="Remover la asociación de un set de mangas a una máquina")
def remove_compatibility(machine_id: int, sleeve_set_id: int):
    if not get_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    if not get_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    if remove_machine_sleeve_set_compatibility(machine_id, sleeve_set_id):
        return {"message": "Compatibility removed successfully"}
    raise HTTPException(status_code=404, detail="Compatibility not found")

@app.get("/machines/{machine_id}/compatible_sleeve_sets/", response_model=List[SleeveSet], summary="Obtener sets de mangas compatibles con una máquina")
def get_compatible_sleeve_sets(machine_id: int):
    if not get_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return get_compatible_sleeve_sets_for_machine(machine_id)

@app.get("/sleeve_sets/{sleeve_set_id}/compatible_machines/", response_model=List[Machine], summary="Obtener máquinas compatibles con un set de mangas")
def get_compatible_machines(sleeve_set_id: int):
    if not get_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    return get_compatible_machines_for_sleeve_set(sleeve_set_id)


@app.get("/optimization_results/latest/{algorithm_type}", response_model=Optional[OptimizationResult], summary="Obtener el último resultado de optimización por tipo de algoritmo")
def get_latest_optimization_result_by_algorithm_endpoint(algorithm_type: str):
    return get_latest_optimization_result_by_algorithm(algorithm_type)

async def _process_optimization_request(file: UploadFile, optimizer_func, algorithm_type: str):
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        optimized_schedule, total_time, total_cost = optimizer_func(df)

        # Formatea el cronograma optimizado para la respuesta JSON
        # Asegura que los tipos de datos sean compatibles con JSON (ej. float en lugar de numpy.float64)
        schedule_per_machine_formatted = {}
        for machine, schedule_list in optimized_schedule.items():
            schedule_per_machine_formatted[machine] = []
            for job in schedule_list:
                formatted_job = {k: (float(v) if isinstance(v, (int, float, np.number)) else v) for k, v in job.items()}
                schedule_per_machine_formatted[machine].append(formatted_job)

        current_time = datetime.datetime.now().isoformat()
        create_optimization_result(
            algorithm_type=algorithm_type,
            timestamp=current_time,
            total_time=total_time,
            total_cost=total_cost,
            schedule_details=json.dumps(schedule_per_machine_formatted)
        )

        file_hash = hashlib.md5(contents).hexdigest()
        create_uploaded_file_info(
            filename=file.filename,
            upload_timestamp=current_time,
            file_hash=file_hash
        )

        return {
            "optimized_schedule": schedule_per_machine_formatted
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing column in Excel file: {e}. Please ensure all required columns are present.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during optimization: {str(e)}")

@app.post("/upload/", summary="Optimizar cronograma con algoritmo codicioso",
          response_description="Cronograma optimizado por máquina.")
async def create_upload_file(file: UploadFile = File(...)):
    return await _process_optimization_request(file, optimize_greedy, "Greedy")

@app.post("/upload-ga/", summary="Optimizar cronograma con algoritmo genético",
          response_description="Cronograma optimizado y resumen original por máquina.")
async def create_upload_file_ga(file: UploadFile = File(...)):
    return await _process_optimization_request(file, optimize_genetic, "Genetic")
