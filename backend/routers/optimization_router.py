from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pandas as pd
import io

from ..services.optimization_service import OptimizationService

router = APIRouter(
    tags=["Optimization"]
)

@router.post("/upload/", summary="Optimizar cronograma con algoritmo codicioso",
          response_description="Cronograma optimizado por máquina.")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Initialize the service and run the optimization
        optimization_service = OptimizationService()
        optimized_schedule, summary = optimization_service.run_greedy_optimization(df)

        # Here you could re-integrate database persistence if needed

        return {
            "optimized_schedule": optimized_schedule,
            "summary": summary
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing column in Excel file: {e}. Please ensure all required columns are present.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during optimization: {str(e)}")

@router.post("/upload-ga/", summary="Optimizar cronograma con algoritmo genético",
          response_description="Cronograma optimizado por máquina.")
async def create_upload_file_ga(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        optimization_service = OptimizationService()
        optimized_schedule, summary = optimization_service.run_genetic_optimization(df)

        return {
            "optimized_schedule": optimized_schedule,
            "summary": summary
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing column in Excel file: {e}. Please ensure all required columns are present.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during optimization: {str(e)}")

