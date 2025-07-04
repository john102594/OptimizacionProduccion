from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

from .optimizers.greedy_optimizer import optimize_greedy
from .optimizers.genetic_optimizer import optimize_genetic

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Production Optimizer API"}

@app.post("/upload/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Assuming the file is an excel file
    try:
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')

        # We assume column names are in Spanish as per the problem description.
        # Lower-casing and replacing spaces for robustness.
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Calculate original summary per machine
        original_summary_per_machine = {}
        for machine in df['maquina_sugerida'].unique():
            machine_df = df[df['maquina_sugerida'] == machine]
            original_summary_per_machine[machine] = {
                "num_references": int(len(machine_df)),
                "total_meters": float(machine_df['metros_requeridos'].sum())
            }

        optimized_schedule = optimize_greedy(df)

        return {
            "optimized_schedule": optimized_schedule,
            "original_summary": original_summary_per_machine
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload-ga/")
async def create_upload_file_ga(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Calculate original summary per machine
        original_summary_per_machine = {}
        for machine in df['maquina_sugerida'].unique():
            machine_df = df[df['maquina_sugerida'] == machine]
            original_summary_per_machine[machine] = {
                "num_references": int(len(machine_df)),
                "total_meters": float(machine_df['metros_requeridos'].sum())
            }

        optimized_schedule_ga = optimize_genetic(df)

        # Formatear el schedule_per_machine para la respuesta
        schedule_per_machine_formatted = {}
        for machine, schedule_list in optimized_schedule_ga.items():
            schedule_per_machine_formatted[machine] = []
            for job in schedule_list:
                schedule_per_machine_formatted[machine].append({
                    'orden': job['orden'],
                    'referencia': job['referencia'],
                    'tipo_de_impresion': job['tipo_de_impresion'],
                    'diametro_de_manga': job['diametro_de_manga'],
                    'metros_requeridos': job['metros_requeridos'],
                    'velocidad_sugerida_m_min': job['velocidad_sugerida_m_min'],
                    'tiempo_estimado_horas': job['tiempo_estimado_horas'],
                    'tiempo_de_cambio_horas': job['tiempo_de_cambio_horas'],
                    'hora_inicio': job['hora_inicio'],
                    'hora_fin': job['hora_fin']
                })

        return {
            "optimized_schedule": schedule_per_machine_formatted,
            "original_summary": original_summary_per_machine
        }
    except Exception as e:
        return {"error": str(e)}