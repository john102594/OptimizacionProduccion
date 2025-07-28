from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pandas as pd
import io
from typing import Dict, List, Any

from ..services.optimization_service import OptimizationService
from ..models.domain import Job, MachineSchedule
from ..utils.setup_utils import get_setup_time

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

@router.post("/recalculate-schedule/", summary="Recalculate schedule times based on a given order",
          response_description="Recalculated schedule with updated times.")
async def recalculate_schedule(schedule_data: Dict[str, List[Dict[str, Any]]]):
    try:
        # Reconstruct MachineSchedule objects from the received data
        machine_schedules = {}
        for machine_name, jobs_data in schedule_data.items():
            machine_schedule = MachineSchedule(machine_name)
            # Manually add jobs to the schedule to trigger time calculations
            for job_data in jobs_data:
                job = Job(job_data) # Create Job object from received data
                # We need to get the setup time here, similar to how optimizers do it
                last_type = machine_schedule.get_last_impression_type()
                setup_time = get_setup_time(last_type, job.tipo_de_impresion)
                machine_schedule.add_job(job, setup_time)
            machine_schedules[machine_name] = machine_schedule

        # Format the results for the response (similar to OptimizationService)
        final_schedule = {name: schedule.to_dict_list() for name, schedule in machine_schedules.items()}
        total_time = max([schedule.get_current_time() for schedule in machine_schedules.values()] or [0])

        # Recalculate summary
        summary = {
            'total_time': round(total_time, 2),
            'unscheduled_jobs': 0, # Assuming all jobs in the provided schedule are scheduled
            'machine_summary': []
        }

        for name, schedule in machine_schedules.items():
            summary['machine_summary'].append({
                'machine': name,
                'total_time': round(schedule.get_current_time(), 2),
                'total_meters': schedule.get_total_meters(),
                'setup_time': round(sum(job['tiempo_de_cambio_horas'] for job in schedule.to_dict_list()), 2),
                'num_jobs': len(schedule.jobs)
            })

        return {
            "optimized_schedule": final_schedule,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recalculation: {str(e)}")

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

