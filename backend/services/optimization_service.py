import pandas as pd
from typing import Dict

from ..models.domain import Job, MachineSchedule
from ..optimizers.greedy_optimizer import optimize_greedy
from ..optimizers.genetic_optimizer3 import optimize_genetic

class OptimizationService:
    def run_greedy_optimization(self, df: pd.DataFrame):
        # 1. Convert DataFrame rows to Job objects
        jobs = [Job(row) for _, row in df.iterrows()]

        # 2. Initialize MachineSchedule objects
        machine_names = df['maquina_sugerida'].unique()
        machine_schedules = {name: MachineSchedule(name) for name in machine_names}

        # 3. Run the optimizer (it will modify machine_schedules in place)
        unscheduled_jobs_count = optimize_greedy(jobs, machine_schedules)

        # 4. Format the results for the response
        final_schedule = {name: schedule.to_dict_list() for name, schedule in machine_schedules.items()}
        total_time = max([schedule.get_current_time() for schedule in machine_schedules.values()] or [0])

        # 5. Calculate summary
        summary = {
            'total_time': round(total_time, 2),
            'unscheduled_jobs': unscheduled_jobs_count,
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

        return final_schedule, summary

    def run_genetic_optimization(self, df: pd.DataFrame):
        # The flow is identical to the greedy one, just calling a different optimizer
        jobs = [Job(row) for _, row in df.iterrows()]
        machine_names = df['maquina_sugerida'].unique()
        machine_schedules = {name: MachineSchedule(name) for name in machine_names}

        unscheduled_jobs_count = optimize_genetic(jobs, machine_schedules)

        final_schedule = {name: schedule.to_dict_list() for name, schedule in machine_schedules.items()}
        total_time = max([schedule.get_current_time() for schedule in machine_schedules.values()] or [0])

        summary = {
            'total_time': round(total_time, 2),
            'unscheduled_jobs': unscheduled_jobs_count,
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

        return final_schedule, summary

    # Note: The genetic optimization flow would need a similar refactoring.
    # The database methods below are kept for persistence, but are not used in the current optimization flow.

    def create_optimization_result(self, algorithm_type: str, timestamp: str, total_time: float, total_cost: float, schedule_details: str) -> Dict[str, any]:
        # This method would need to be integrated back into the router if persistence is needed
        pass

    def get_optimization_result(self, result_id: int):
        pass
