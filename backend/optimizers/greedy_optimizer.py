import pandas as pd
from ..utils.setup_utils import get_setup_time

from ..utils.setup_utils import get_setup_time
from ..models.domain import Job, MachineSchedule
from typing import List, Dict

def optimize_greedy(jobs: List[Job], machine_schedules: Dict[str, MachineSchedule]):
    # Sort jobs by criticality and then by impression type as a pre-processing step
    jobs.sort(key=lambda j: (j.nivel_de_criticidad, j.tipo_de_impresion), reverse=True)

    scheduled_job_indices = set()
    available_jobs = list(jobs)

    while len(scheduled_job_indices) < len(jobs):
        best_job_to_schedule = None
        best_machine_for_job = None
        min_setup_time = float('inf')

        # In each iteration, find the best possible job to schedule next across all machines
        for job in available_jobs:
            if job.original_index in scheduled_job_indices:
                continue

            machine_name = job.maquina_sugerida
            machine = machine_schedules[machine_name]
            
            last_type = machine.get_last_impression_type()
            setup_time = get_setup_time(last_type, job.tipo_de_impresion)

            if machine.can_add_job(job, setup_time):
                # Greedy criteria: prioritize by criticality, then by minimum setup time
                if best_job_to_schedule is None or \
                   job.nivel_de_criticidad > best_job_to_schedule.nivel_de_criticidad or \
                   (job.nivel_de_criticidad == best_job_to_schedule.nivel_de_criticidad and setup_time < min_setup_time):
                    
                    best_job_to_schedule = job
                    best_machine_for_job = machine
                    min_setup_time = setup_time

        if best_job_to_schedule:
            # Add the chosen job to the machine's schedule
            best_machine_for_job.add_job(best_job_to_schedule, min_setup_time)
            scheduled_job_indices.add(best_job_to_schedule.original_index)
            available_jobs.remove(best_job_to_schedule)
        else:
            # No more jobs can be scheduled on any machine
            break

    unscheduled_jobs_count = len(jobs) - len(scheduled_job_indices)

    # The machine_schedules dictionary is modified in place, so we don't need to return it
    return unscheduled_jobs_count