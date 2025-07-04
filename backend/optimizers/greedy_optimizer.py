import pandas as pd
from ..utils.setup_utils import get_setup_time

def optimize_greedy(df):
    # Calculate time for each job in hours
    df['tiempo_horas'] = df.apply(
        lambda row: row['metros_requeridos'] / (row['velocidad_sugerida'] * 60) if row['velocidad_sugerida'] > 0 else float('inf'),
        axis=1
    )

    # Calculate efficiency (meters per hour)
    df['eficiencia'] = df.apply(
        lambda row: row['metros_requeridos'] / row['tiempo_horas'] if row['tiempo_horas'] > 0 else 0,
        axis=1
    )

    df_sorted = df.sort_values(
        by=['nivel_de_criticidad', 'eficiencia', 'tipo_de_impresion', 'diametro_de_manga'],
        ascending=[False, False, True, True]
    ).reset_index(drop=True)

    schedule_per_machine = {}
    machine_current_time = {}  # To track current time for each machine
    machine_last_impression_type = {} # To track last impression type for each machine
    
    for machine in df['maquina_sugerida'].unique():
        schedule_per_machine[machine] = []
        machine_current_time[machine] = 0.0
        machine_last_impression_type[machine] = None

    scheduled_job_indices = set()

    while len(scheduled_job_indices) < len(df_sorted):
        best_job_for_machine = {}
        
        for machine in schedule_per_machine.keys():
            current_machine_time = machine_current_time[machine]
            last_type = machine_last_impression_type[machine]
            
            best_candidate_job = None
            min_total_time = float('inf')
            
            for idx, job_row in df_sorted.iterrows():
                if idx in scheduled_job_indices or job_row['maquina_sugerida'] != machine:
                    continue
                
                current_job_type = job_row['tipo_de_impresion']
                setup_time = get_setup_time(last_type, current_job_type)
                
                total_job_duration = job_row['tiempo_horas'] + setup_time
                
                if current_machine_time + total_job_duration <= 24:
                    if best_candidate_job is None or \
                       job_row['nivel_de_criticidad'] > best_candidate_job['nivel_de_criticidad'] or \
                       (job_row['nivel_de_criticidad'] == best_candidate_job['nivel_de_criticidad'] and \
                        job_row['eficiencia'] > best_candidate_job['eficiencia']) or \
                       (job_row['nivel_de_criticidad'] == best_candidate_job['nivel_de_criticidad'] and \
                        job_row['eficiencia'] == best_candidate_job['eficiencia'] and \
                        total_job_duration < min_total_time):
                        
                        best_candidate_job = job_row.copy()
                        best_candidate_job['setup_time_hours'] = setup_time
                        best_candidate_job['total_duration_with_setup'] = total_job_duration
                        min_total_time = total_job_duration
        
            if best_candidate_job is not None:
                best_job_for_machine[machine] = best_candidate_job
        
        if not best_job_for_machine:
            break

        scheduled_this_iteration = False
        for machine, job_to_schedule in best_job_for_machine.items():
            if job_to_schedule.name not in scheduled_job_indices:
                current_machine_time = machine_current_time[machine]
                
                job = {
                    'orden': len(schedule_per_machine[machine]) + 1,
                    'referencia': job_to_schedule['referencia'],
                    'tipo_de_impresion': job_to_schedule['tipo_de_impresion'],
                    'diametro_de_manga': float(job_to_schedule['diametro_de_manga']),
                    'metros_requeridos': float(job_to_schedule['metros_requeridos']),
                    'velocidad_sugerida_m_min': float(job_to_schedule['velocidad_sugerida']),
                    'tiempo_estimado_horas': float(round(job_to_schedule['tiempo_horas'], 2)),
                    'tiempo_de_cambio_horas': float(round(job_to_schedule['setup_time_hours'], 2)),
                    'hora_inicio': float(round(current_machine_time, 2)),
                    'hora_fin': float(round(current_machine_time + job_to_schedule['total_duration_with_setup'], 2))
                }
                schedule_per_machine[machine].append(job)
                machine_current_time[machine] += job_to_schedule['total_duration_with_setup']
                machine_last_impression_type[machine] = job_to_schedule['tipo_de_impresion']
                scheduled_job_indices.add(job_to_schedule.name)
                scheduled_this_iteration = True
        
        if not scheduled_this_iteration and len(scheduled_job_indices) < len(df_sorted):
            break

    return schedule_per_machine