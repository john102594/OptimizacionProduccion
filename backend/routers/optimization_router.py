from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import json
import datetime
import hashlib
import pandas as pd
import io
import numpy as np

from ..models.optimization_result import OptimizationResult
from ..models.uploaded_file import UploadedFileInfo
from ..services.optimization_service import OptimizationService
from ..services.uploaded_file_service import UploadedFileService
from ..optimizers.greedy_optimizer import optimize_greedy
from ..optimizers.genetic_optimizer3 import optimize_genetic

router = APIRouter(
    tags=["Optimization"]
)

async def _process_optimization_request(file: UploadFile, optimizer_func, algorithm_type: str, optimization_service: OptimizationService, uploaded_file_service: UploadedFileService):
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        optimized_schedule, total_time, total_cost = optimizer_func(df)

        schedule_per_machine_formatted = {}
        for machine, schedule_list in optimized_schedule.items():
            schedule_per_machine_formatted[machine] = []
            for job in schedule_list:
                formatted_job = {k: (float(v) if isinstance(v, (int, float, np.number)) else v) for k, v in job.items()}
                schedule_per_machine_formatted[machine].append(formatted_job)

        current_time = datetime.datetime.now().isoformat()
        optimization_service.create_optimization_result(
            algorithm_type=algorithm_type,
            timestamp=current_time,
            total_time=total_time,
            total_cost=total_cost,
            schedule_details=json.dumps(schedule_per_machine_formatted)
        )

        file_hash = hashlib.md5(contents).hexdigest()
        uploaded_file_service.create_uploaded_file_info(
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

@router.post("/upload/", summary="Optimizar cronograma con algoritmo codicioso",
          response_description="Cronograma optimizado por máquina.")
async def create_upload_file(file: UploadFile = File(...),
                             optimization_service: OptimizationService = Depends(OptimizationService),
                             uploaded_file_service: UploadedFileService = Depends(UploadedFileService)):
    return await _process_optimization_request(file, optimize_greedy, "Greedy", optimization_service, uploaded_file_service)

@router.post("/upload-ga/", summary="Optimizar cronograma con algoritmo genético",
          response_description="Cronograma optimizado por máquina.")
async def create_upload_file_ga(file: UploadFile = File(...),
                                optimization_service: OptimizationService = Depends(OptimizationService),
                                uploaded_file_service: UploadedFileService = Depends(UploadedFileService)):
    return await _process_optimization_request(file, optimize_genetic, "Genetic", optimization_service, uploaded_file_service)

@router.get("/optimization_results/latest/{algorithm_type}", response_model=Optional[OptimizationResult], summary="Obtener el último resultado de optimización por tipo de algoritmo")
def get_latest_optimization_result_by_algorithm_endpoint(algorithm_type: str, optimization_service: OptimizationService = Depends(OptimizationService)):
    return optimization_service.get_latest_optimization_result_by_algorithm(algorithm_type)
