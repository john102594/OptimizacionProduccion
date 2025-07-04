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

def calculate_fitness(job_order, jobs_df, total_jobs, weights=None):
    """
    Función de fitness mejorada optimizada para maximizar metros producidos
    """
    if weights is None:
        weights = {'metros_producidos': 0.7, 'eficiencia_tiempo': 0.2, 'setup_time': 0.1}
    
    schedule_per_machine, makespan, unscheduled_jobs_count = assign_jobs_to_machines(jobs_df, job_order)
    
    # Calcular metros totales producidos (solo trabajos programados)
    total_metros_producidos = 0
    total_metros_posibles = jobs_df['metros_requeridos'].sum()
    
    job_data_map = {idx: row for idx, row in jobs_df.iterrows()}
    
    # Sumar metros de trabajos programados
    for job_idx in job_order:
        job_row = job_data_map[job_idx]
        machine = job_row['maquina_sugerida']
        
        # Verificar si el trabajo fue programado
        job_scheduled = False
        for scheduled_job in schedule_per_machine.get(machine, []):
            if scheduled_job['referencia'] == job_row['referencia']:
                total_metros_producidos += job_row['metros_requeridos']
                job_scheduled = True
                break
    
    # Manejar casos extremos
    if total_metros_producidos == 0:
        return 0.0
    
    # Calcular tiempo total de setup
    setup_time_total = 0
    for i in range(1, len(job_order)):
        prev_job = job_data_map[job_order[i-1]]
        curr_job = job_data_map[job_order[i]]
        
        if prev_job['maquina_sugerida'] == curr_job['maquina_sugerida']:
            setup_time_total += get_setup_time(
                prev_job['tipo_de_impresion'], 
                curr_job['tipo_de_impresion']
            )
    
    # Componentes del fitness
    # 1. Porcentaje de metros producidos (objetivo principal)
    metros_score = total_metros_producidos / total_metros_posibles
    
    # 2. Eficiencia de tiempo (metros por hora)
    tiempo_efectivo = makespan - setup_time_total if makespan > 0 else 1
    eficiencia_tiempo = total_metros_producidos / tiempo_efectivo if tiempo_efectivo > 0 else 0
    eficiencia_normalizada = min(1.0, eficiencia_tiempo / 1000)  # Normalizar a escala 0-1
    
    # 3. Penalización por tiempo de setup
    setup_penalty = 1 / (setup_time_total + 1)
    
    # Fitness ponderado
    fitness = (weights['metros_producidos'] * metros_score + 
               weights['eficiencia_tiempo'] * eficiencia_normalizada +
               weights['setup_time'] * setup_penalty)
    
    return fitness

def initialize_population(pop_size, num_jobs, jobs_df):
    """
    Inicialización mejorada con heurísticas orientadas a maximizar metros
    """
    population = []
    
    # 20% población aleatoria
    for _ in range(pop_size // 5):
        chromosome = list(range(num_jobs))
        random.shuffle(chromosome)
        population.append(chromosome)
    
    # 25% ordenado por metros requeridos (highest first) - priorizar trabajos grandes
    metros_sorted = sorted(range(num_jobs), 
                          key=lambda i: jobs_df.iloc[i]['metros_requeridos'], 
                          reverse=True)
    population.append(metros_sorted)
    
    # 25% ordenado por eficiencia (metros/hora) - priorizar trabajos eficientes
    efficiency_sorted = sorted(range(num_jobs), 
                              key=lambda i: jobs_df.iloc[i]['eficiencia'], 
                              reverse=True)
    population.append(efficiency_sorted)
    
    # 15% ordenado por densidad de valor (metros/tiempo) - balance metros vs tiempo
    value_density_sorted = sorted(range(num_jobs), 
                                 key=lambda i: jobs_df.iloc[i]['metros_requeridos'] / max(jobs_df.iloc[i]['tiempo_horas'], 0.1), 
                                 reverse=True)
    population.append(value_density_sorted)
    
    # 15% ordenado por máquina y tipo para minimizar setups
    machine_type_sorted = sorted(range(num_jobs), 
                                key=lambda i: (jobs_df.iloc[i]['maquina_sugerida'], 
                                             jobs_df.iloc[i]['tipo_de_impresion']))
    population.append(machine_type_sorted)
    
    # Llenar el resto con variaciones de las mejores heurísticas
    base_solutions = [metros_sorted, efficiency_sorted, value_density_sorted]
    while len(population) < pop_size:
        base = random.choice(base_solutions).copy()
        # Mutación ligera manteniendo los trabajos más importantes al principio
        mutation_intensity = random.randint(1, min(3, len(base) // 10))
        for _ in range(mutation_intensity):
            # Dar más probabilidad de mutación a la segunda mitad
            if random.random() < 0.7:
                idx1 = random.randint(len(base) // 2, len(base) - 1)
                idx2 = random.randint(len(base) // 2, len(base) - 1)
            else:
                idx1, idx2 = random.sample(range(len(base)), 2)
            base[idx1], base[idx2] = base[idx2], base[idx1]
        population.append(base)
    
    return population

def selection(population, fitnesses, num_parents):
    """
    Selección por torneo mejorada con diversidad
    """
    parents = []
    tournament_size = max(3, len(population) // 10)  # Torneo adaptativo
    
    for _ in range(num_parents):
        # Selección por torneo
        contenders_indices = random.sample(range(len(population)), tournament_size)
        best_contender_index = max(contenders_indices, key=lambda i: fitnesses[i])
        parents.append(population[best_contender_index])
    
    return parents

def crossover(parent1, parent2):
    """
    Crossover mejorado con múltiples operadores
    """
    size = len(parent1)
    
    # Seleccionar operador de crossover aleatoriamente
    crossover_type = random.choice(['order', 'pmx', 'cycle'])
    
    if crossover_type == 'order':
        return order_crossover(parent1, parent2)
    elif crossover_type == 'pmx':
        return pmx_crossover(parent1, parent2)
    else:
        return cycle_crossover(parent1, parent2)

def order_crossover(parent1, parent2):
    """Order Crossover (OX)"""
    size = len(parent1)
    child1 = [-1] * size
    child2 = [-1] * size

    start, end = sorted(random.sample(range(size), 2))

    child1[start:end] = parent1[start:end]
    child2[start:end] = parent2[start:end]

    # Llenar child1
    remaining = [x for x in parent2 if x not in child1]
    idx = 0
    for i in range(size):
        if child1[i] == -1:
            child1[i] = remaining[idx]
            idx += 1

    # Llenar child2
    remaining = [x for x in parent1 if x not in child2]
    idx = 0
    for i in range(size):
        if child2[i] == -1:
            child2[i] = remaining[idx]
            idx += 1

    return child1, child2

def pmx_crossover(parent1, parent2):
    """Partially Mapped Crossover (PMX)"""
    size = len(parent1)
    child1 = parent1.copy()
    child2 = parent2.copy()

    start, end = sorted(random.sample(range(size), 2))

    # Intercambiar segmentos
    for i in range(start, end):
        # Encontrar posiciones de los elementos a intercambiar
        pos1 = child1.index(parent2[i])
        pos2 = child2.index(parent1[i])
        
        # Intercambiar
        child1[i], child1[pos1] = child1[pos1], child1[i]
        child2[i], child2[pos2] = child2[pos2], child2[i]

    return child1, child2

def cycle_crossover(parent1, parent2):
    """Cycle Crossover (CX)"""
    size = len(parent1)
    child1 = [-1] * size
    child2 = [-1] * size
    
    visited = [False] * size
    
    for start in range(size):
        if not visited[start]:
            # Crear ciclo
            cycle = []
            current = start
            while not visited[current]:
                visited[current] = True
                cycle.append(current)
                current = parent1.index(parent2[current])
            
            # Asignar ciclo alternadamente
            if len([c for c in range(start) if visited[c]]) % 2 == 0:
                for pos in cycle:
                    child1[pos] = parent1[pos]
                    child2[pos] = parent2[pos]
            else:
                for pos in cycle:
                    child1[pos] = parent2[pos]
                    child2[pos] = parent1[pos]
    
    return child1, child2

def mutate(chromosome, mutation_rate):
    """
    Mutación mejorada con múltiples operadores
    """
    if random.random() < mutation_rate:
        mutation_type = random.choice(['swap', 'insert', 'invert'])
        
        if mutation_type == 'swap':
            idx1, idx2 = random.sample(range(len(chromosome)), 2)
            chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
        
        elif mutation_type == 'insert':
            # Insertar elemento en nueva posición
            from_idx = random.randint(0, len(chromosome) - 1)
            to_idx = random.randint(0, len(chromosome) - 1)
            element = chromosome.pop(from_idx)
            chromosome.insert(to_idx, element)
        
        elif mutation_type == 'invert':
            # Invertir subsecuencia
            start, end = sorted(random.sample(range(len(chromosome)), 2))
            chromosome[start:end] = chromosome[start:end][::-1]
    
    return chromosome

def optimize_genetic(df):
    """
    Algoritmo genético mejorado optimizado para maximizar metros producidos
    """
    # Preparar datos
    df['tiempo_horas'] = df.apply(
        lambda row: row['metros_requeridos'] / (row['velocidad_sugerida'] * 60) if row['velocidad_sugerida'] > 0 else float('inf'),
        axis=1
    )
    
    df['eficiencia'] = df.apply(
        lambda row: row['metros_requeridos'] / row['tiempo_horas'] if row['tiempo_horas'] > 0 else 0,
        axis=1
    )

    # Parámetros adaptativos
    POPULATION_SIZE = min(100, max(50, len(df) * 2))
    MAX_GENERATIONS = 200
    BASE_MUTATION_RATE = 0.1
    NUM_PARENTS = POPULATION_SIZE // 2
    STAGNATION_LIMIT = 20  # Generaciones sin mejora
    
    num_jobs = len(df)
    
    # Inicialización mejorada
    population = initialize_population(POPULATION_SIZE, num_jobs, df)
    
    best_chromosome = None
    best_fitness = -1.0
    best_metros_producidos = 0
    stagnation_count = 0
    mutation_rate = BASE_MUTATION_RATE
    
    # Cache para fitness
    fitness_cache = {}
    
    for generation in range(MAX_GENERATIONS):
        # Calcular fitness con cache
        fitnesses = []
        for chromosome in population:
            key = tuple(chromosome)
            if key not in fitness_cache:
                fitness_cache[key] = calculate_fitness(chromosome, df, num_jobs)
            fitnesses.append(fitness_cache[key])
        
        # Actualizar mejor solución
        current_best_fitness = max(fitnesses)
        current_best_chromosome = population[fitnesses.index(current_best_fitness)]
        
        # Calcular metros producidos para la mejor solución actual
        schedule_temp, _, _ = assign_jobs_to_machines(df, current_best_chromosome)
        metros_actuales = 0
        for machine_schedule in schedule_temp.values():
            for job in machine_schedule:
                metros_actuales += job['metros_requeridos']
        
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_chromosome = current_best_chromosome.copy()
            best_metros_producidos = metros_actuales
            stagnation_count = 0
        else:
            stagnation_count += 1
        
        # Adaptación de parámetros
        if stagnation_count > STAGNATION_LIMIT:
            mutation_rate = min(0.3, mutation_rate * 1.1)  # Aumentar mutación
            stagnation_count = 0
        else:
            mutation_rate = max(0.05, mutation_rate * 0.99)  # Disminuir mutación
        
        # Criterio de parada temprana
        if generation > 50 and stagnation_count > STAGNATION_LIMIT * 2:
            break
        
        # Selección
        parents = selection(population, fitnesses, NUM_PARENTS)
        
        # Crear nueva generación
        next_population = []
        
        # Elitismo: mantener mejores soluciones
        elite_size = POPULATION_SIZE // 10
        elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:elite_size]
        for idx in elite_indices:
            next_population.append(population[idx].copy())
        
        # Generar descendencia
        while len(next_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(parents, 2)
            child1, child2 = crossover(parent1, parent2)
            
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)
            
            next_population.append(child1)
            if len(next_population) < POPULATION_SIZE:
                next_population.append(child2)
        
        population = next_population
        
        # Limitar tamaño del cache
        if len(fitness_cache) > 1000:
            fitness_cache.clear()
    
    # Generar schedule final
    optimized_schedule_ga, makespan, unscheduled = assign_jobs_to_machines(df, best_chromosome)
    
    return optimized_schedule_ga