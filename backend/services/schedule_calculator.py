from ..utils.setup_utils import get_setup_time

def calculate_schedule_times(schedule_per_machine):
    enriched_schedule = {}
    total_time = 0.0

    for machine, jobs in schedule_per_machine.items():
        machine_current_time = 0.0
        last_impression_type = None
        enriched_jobs = []

        for i, job in enumerate(jobs):
            # Calculate job duration
            tiempo_horas = job['metros_requeridos'] / (job['velocidad_sugerida_m_min'] * 60) if job['velocidad_sugerida_m_min'] > 0 else float('inf')

            # Calculate setup time
            setup_time = get_setup_time(last_impression_type, job['tipo_de_impresion'])
            total_job_duration = tiempo_horas + setup_time

            # Calculate start and end times
            hora_inicio = machine_current_time
            hora_fin = machine_current_time + total_job_duration

            enriched_job = job.copy()
            enriched_job.update({
                'orden': i + 1,
                'tiempo_estimado_horas': round(tiempo_horas, 2),
                'tiempo_de_cambio_horas': round(setup_time, 2),
                'hora_inicio': round(hora_inicio, 2),
                'hora_fin': round(hora_fin, 2)
            })
            enriched_jobs.append(enriched_job)

            # Update machine state for next job
            machine_current_time = hora_fin
            last_impression_type = job['tipo_de_impresion']
        
        enriched_schedule[machine] = enriched_jobs
        if enriched_jobs:
            total_time = max(total_time, enriched_jobs[-1]['hora_fin'])

    return enriched_schedule, total_time
