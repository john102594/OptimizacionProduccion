import random
import numpy as np
from ..utils.setup_utils import get_setup_time

def assign_jobs_to_machines(jobs_df, job_order):
    schedule_per_machine = {}
    machine_current_time = {}
    machine_last_impression_type = {}
    
    for machine in jobs_df['maquina_sugerida'].unique():
        schedule_per_machine[machine] = []
        machine_current_time[machine] = 0.0
        machine_last_impression_type[machine] = None

    unscheduled_jobs_count = 0
    job_data_map = {idx: row for idx, row in jobs_df.iterrows()}

    for job_idx in job_order:
        job_row = job_data_map[job_idx]
        machine = job_row['maquina_sugerida']
        current_machine_time = machine_current_time[machine]
        last_type = machine_last_impression_type[machine]
        
        current_job_type = job_row['tipo_de_impresion']
        setup_time = get_setup_time(last_type, current_job_type)
        
        total_job_duration = job_row['tiempo_horas'] + setup_time
        
        if current_machine_time + total_job_duration <= 24:
            job = {
                'orden': len(schedule_per_machine[machine]) + 1,
                'referencia': job_row['referencia'],
                'tipo_de_impresion': job_row['tipo_de_impresion'],
                'diametro_de_manga': float(job_row['diametro_de_manga']),
                'metros_requeridos': float(job_row['metros_requeridos']),
                'velocidad_sugerida_m_min': float(job_row['velocidad_sugerida']),
                'tiempo_estimado_horas': float(round(job_row['tiempo_horas'], 2)),
                'tiempo_de_cambio_horas': float(round(setup_time, 2)),
                'hora_inicio': float(round(current_machine_time, 2)),
                'hora_fin': float(round(current_machine_time + total_job_duration, 2))
            }
            schedule_per_machine[machine].append(job)
            machine_current_time[machine] += total_job_duration
            machine_last_impression_type[machine] = job_row['tipo_de_impresion']
        else:
            unscheduled_jobs_count += 1

    makespan = max(machine_current_time.values()) if machine_current_time else 0.0
    
    return schedule_per_machine, makespan, unscheduled_jobs_count

def calculate_fitness(job_order, jobs_df, total_jobs):
    """
    Función de fitness simple optimizada para metros producidos
    """
    schedule_per_machine, makespan, unscheduled_jobs_count = assign_jobs_to_machines(jobs_df, job_order)
    
    # Calcular metros totales producidos
    total_metros_producidos = 0
    for machine_schedule in schedule_per_machine.values():
        for job in machine_schedule:
            total_metros_producidos += job['metros_requeridos']
    
    # Penalización por trabajos no programados
    penalty = unscheduled_jobs_count * 1000
    
    # Fitness basado en metros producidos
    if total_metros_producidos == 0:
        return 0.0
    
    # Bonificación por eficiencia de tiempo
    time_bonus = 1.0
    if makespan > 0:
        time_bonus = min(2.0, 24.0 / makespan)  # Bonifica si termina antes
    
    fitness = total_metros_producidos * time_bonus - penalty
    return max(0.0, fitness)

def initialize_population_fast(pop_size, num_jobs, jobs_df):
    """
    Inicialización rápida con heurísticas básicas
    """
    population = []
    
    # 50% población aleatoria
    for _ in range(pop_size // 2):
        chromosome = list(range(num_jobs))
        random.shuffle(chromosome)
        population.append(chromosome)
    
    # 25% ordenado por metros (mayor primero)
    metros_sorted = sorted(range(num_jobs), 
                          key=lambda i: jobs_df.iloc[i]['metros_requeridos'], 
                          reverse=True)
    population.append(metros_sorted)
    
    # 25% ordenado por eficiencia
    efficiency_sorted = sorted(range(num_jobs), 
                              key=lambda i: jobs_df.iloc[i]['eficiencia'], 
                              reverse=True)
    population.append(efficiency_sorted)
    
    # Llenar resto con variaciones simples
    base_solutions = [metros_sorted, efficiency_sorted]
    while len(population) < pop_size:
        base = random.choice(base_solutions).copy()
        # Mutación simple
        idx1, idx2 = random.sample(range(len(base)), 2)
        base[idx1], base[idx2] = base[idx2], base[idx1]
        population.append(base)
    
    return population

def selection(population, fitnesses, num_parents):
    """
    Selección por torneo simple
    """
    parents = []
    for _ in range(num_parents):
        tournament_size = 3
        contenders_indices = random.sample(range(len(population)), tournament_size)
        
        best_contender_index = contenders_indices[0]
        for i in contenders_indices:
            if fitnesses[i] > fitnesses[best_contender_index]:
                best_contender_index = i
        parents.append(population[best_contender_index])
    return parents

def crossover(parent1, parent2):
    """
    Crossover simple (Order Crossover)
    """
    size = len(parent1)
    child1 = [-1] * size
    child2 = [-1] * size

    start, end = sorted(random.sample(range(size), 2))

    child1[start:end] = parent1[start:end]
    child2[start:end] = parent2[start:end]

    current_parent2_pos = 0
    for i in range(size):
        if child1[i] == -1:
            while parent2[current_parent2_pos] in child1:
                current_parent2_pos += 1
            child1[i] = parent2[current_parent2_pos]
            current_parent2_pos += 1

    current_parent1_pos = 0
    for i in range(size):
        if child2[i] == -1:
            while parent1[current_parent1_pos] in child2:
                current_parent1_pos += 1
            child2[i] = parent1[current_parent1_pos]
            current_parent1_pos += 1

    return child1, child2

def mutate(chromosome, mutation_rate):
    """
    Mutación simple por intercambio
    """
    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(len(chromosome)), 2)
        chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
    return chromosome

def optimize_genetic(df):
    """
    Algoritmo genético optimizado para metros pero manteniendo velocidad
    """
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

    # Parámetros similares al original pero con inicialización mejorada
    POPULATION_SIZE = 50
    NUM_GENERATIONS = 100
    MUTATION_RATE = 0.1
    NUM_PARENTS = 20

    num_jobs = len(df)

    # Inicialización mejorada pero rápida
    population = initialize_population_fast(POPULATION_SIZE, num_jobs, df)

    best_chromosome = None
    best_fitness = -1.0

    for generation in range(NUM_GENERATIONS):
        # Usar la nueva función de fitness orientada a metros
        fitnesses = [calculate_fitness(chromosome, df, num_jobs) for chromosome in population]

        current_best_fitness = max(fitnesses)
        current_best_chromosome = population[fitnesses.index(current_best_fitness)]

        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_chromosome = current_best_chromosome

        parents = selection(population, fitnesses, NUM_PARENTS)

        next_population = []
        if best_chromosome is not None:
            next_population.append(best_chromosome)

        while len(next_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(parents, 2)
            child1, child2 = crossover(parent1, parent2)
            
            child1 = mutate(child1, MUTATION_RATE)
            child2 = mutate(child2, MUTATION_RATE)
            
            next_population.append(child1)
            if len(next_population) < POPULATION_SIZE:
                next_population.append(child2)
        
        population = next_population

    optimized_schedule_ga, _, _ = assign_jobs_to_machines(df, best_chromosome)

    return optimized_schedule_ga