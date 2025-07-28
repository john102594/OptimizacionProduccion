import random
from typing import List, Dict
from ..utils.setup_utils import get_setup_time
from ..models.domain import Job, MachineSchedule

def optimize_greedy(jobs: List[Job], machine_schedules: Dict[str, MachineSchedule]):
    print(f"DEBUG: optimize_greedy started. Total jobs: {len(jobs)}, Machines: {len(machine_schedules)}")

    scheduled_job_indices = set()
    candidate_jobs = {job.original_index: job for job in jobs}

    iteration = 0
    while len(scheduled_job_indices) < len(jobs):
        iteration += 1
        print(f"\nDEBUG: Iteration {iteration}. Candidate jobs remaining: {len(candidate_jobs)}")

        best_job_to_schedule = None
        best_machine_for_job = None
        min_total_duration_for_best = float('inf')

        # Iterate through all machines and all unscheduled jobs to find the best fit
        for machine_name, machine in machine_schedules.items():
            last_type = machine.get_last_impression_type()
            print(f"DEBUG:   Checking machine {machine_name}. Last type: {last_type}, Current time: {machine.get_current_time()}")

            for job_idx, job in candidate_jobs.items():
                if job.maquina_sugerida != machine_name: # Only consider jobs for this machine
                    continue

                setup_time = get_setup_time(last_type, job.tipo_de_impresion)
                job_duration = job.get_duration_hours()
                total_duration = job_duration + setup_time

                if machine.can_add_job(job, setup_time):
                    # Greedy criteria: prioritize by criticality, then by total duration (job + setup)
                    if best_job_to_schedule is None or \
                       job.nivel_de_criticidad > best_job_to_schedule.nivel_de_criticidad or \
                       (job.nivel_de_criticidad == best_job_to_schedule.nivel_de_criticidad and total_duration < min_total_duration_for_best):
                        
                        best_job_to_schedule = job
                        best_machine_for_job = machine
                        min_total_duration_for_best = total_duration
                        print(f"DEBUG:     Found potential best: Job {job.referencia} (Crit: {job.nivel_de_criticidad}, Dur: {total_duration:.2f}) for machine {machine_name}")
        
        if best_job_to_schedule:
            print(f"DEBUG: Selected Job: {best_job_to_schedule.referencia} for Machine: {best_machine_for_job.machine_name}")
            try:
                setup_time_for_add = get_setup_time(best_machine_for_job.get_last_impression_type(), best_job_to_schedule.tipo_de_impresion)
                print(f"DEBUG:   Calculated setup_time_for_add: {setup_time_for_add}")
                best_machine_for_job.add_job(best_job_to_schedule, setup_time_for_add)
                scheduled_job_indices.add(best_job_to_schedule.original_index)
                del candidate_jobs[best_job_to_schedule.original_index] # Remove from candidates
                print(f"DEBUG: Job {best_job_to_schedule.referencia} scheduled. Total scheduled: {len(scheduled_job_indices)}")
            except Exception as e:
                print(f"ERROR: Exception during job addition: {e}")
                import traceback
                traceback.print_exc()
                break # Break the loop to prevent further errors
        else:
            print("DEBUG: No more jobs can be scheduled under current constraints. Breaking loop.")
            break

    unscheduled_jobs_count = len(jobs) - len(scheduled_job_indices)
    print(f"DEBUG: optimize_greedy finished. Unscheduled jobs: {unscheduled_jobs_count}")
    return unscheduled_jobs_count