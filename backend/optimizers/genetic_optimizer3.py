import random
from typing import List, Dict
from ..utils.setup_utils import get_setup_time
from ..models.domain import Job, MachineSchedule

def _assign_chromosome_to_machines(chromosome: List[Job], machine_names: List[str]) -> tuple[Dict[str, MachineSchedule], int]:
    """
    Assigns a sequence of jobs (a chromosome) to fresh machine schedules to evaluate its fitness.
    This is a pure function used for evaluation inside the fitness calculation.
    """
    # For each evaluation, we need a fresh set of machine schedules
    temp_machine_schedules = {name: MachineSchedule(name) for name in machine_names}
    scheduled_job_indices = set()

    for job in chromosome:
        machine = temp_machine_schedules[job.maquina_sugerida]
        last_type = machine.get_last_impression_type()
        setup_time = get_setup_time(last_type, job.tipo_de_impresion)

        if machine.can_add_job(job, setup_time):
            machine.add_job(job, setup_time)
            scheduled_job_indices.add(job.original_index)

    unscheduled_count = len(chromosome) - len(scheduled_job_indices)
    return temp_machine_schedules, unscheduled_count

def _calculate_fitness(chromosome: List[Job], machine_names: List[str]) -> float:
    """
    Fitness function: Maximizes total meters produced and rewards finishing faster.
    Penalizes leaving jobs unscheduled.
    """
    temp_schedules, unscheduled_count = _assign_chromosome_to_machines(chromosome, machine_names)

    total_meters_produced = sum(s.get_total_meters() for s in temp_schedules.values())
    makespan = max([s.get_current_time() for s in temp_schedules.values()] or [0])

    # Calculate total criticality of scheduled jobs
    total_criticality_scheduled = 0
    for machine_schedule in temp_schedules.values():
        for scheduled_item in machine_schedule.jobs:
            total_criticality_scheduled += scheduled_item['job_object'].nivel_de_criticidad

    # Heavy penalty for each unscheduled job
    penalty = unscheduled_count * 0  # This value might need tuning

    # Bonus for finishing early (efficiency)
    time_bonus = 1.0
    # if makespan > 0:
    #     time_bonus = min(2.0, 24.0 / makespan) # Bonus if it finishes in less than 24h

    # Combine all factors into the fitness score
    # Weight criticality to ensure it has a significant impact
    fitness = (total_meters_produced * time_bonus) + (total_criticality_scheduled * 10000) - penalty
    return max(0.0, fitness)

def _initialize_population(pop_size: int, jobs: List[Job]) -> List[List[Job]]:
    """
    Initializes the population with a mix of random and heuristic-based solutions.
    """
    population = []
    
    # 50% of population is purely random
    for _ in range(pop_size // 2):
        chromosome = random.sample(jobs, len(jobs))
        population.append(chromosome)
    
    # 50% is based on a heuristic (sorted by criticality)
    heuristic_chromosome = sorted(jobs, key=lambda j: j.nivel_de_criticidad, reverse=True)
    for _ in range(pop_size - len(population)):
        # Add variations of the heuristic solution
        mutated_chromosome = heuristic_chromosome[:]
        idx1, idx2 = random.sample(range(len(jobs)), 2)
        mutated_chromosome[idx1], mutated_chromosome[idx2] = mutated_chromosome[idx2], mutated_chromosome[idx1]
        population.append(mutated_chromosome)
        
    return population

def _selection(population: List[List[Job]], fitnesses: List[float], num_parents: int) -> List[List[Job]]:
    """Selects the best individuals from the current generation to be parents."""
    parents = []
    for _ in range(num_parents):
        # Tournament selection
        tournament_size = 3
        contender_indices = random.sample(range(len(population)), tournament_size)
        
        best_contender_idx = max(contender_indices, key=lambda i: fitnesses[i])
        parents.append(population[best_contender_idx])
    return parents

def _crossover(parent1: List[Job], parent2: List[Job]) -> tuple[List[Job], List[Job]]:
    """Creates two new child chromosomes from two parents using Order Crossover (OX1)."""
    size = len(parent1)
    child1, child2 = [-1] * size, [-1] * size
    
    start, end = sorted(random.sample(range(size), 2))
    
    # Copy slice from parents to children
    child1[start:end] = parent1[start:end]
    child2[start:end] = parent2[start:end]
    
    # Fill the rest of child1
    parent2_ptr = 0
    for i in range(size):
        if child1[i] == -1:
            while parent2[parent2_ptr] in child1:
                parent2_ptr += 1
            child1[i] = parent2[parent2_ptr]

    # Fill the rest of child2
    parent1_ptr = 0
    for i in range(size):
        if child2[i] == -1:
            while parent1[parent1_ptr] in child2:
                parent1_ptr += 1
            child2[i] = parent1[parent1_ptr]
            
    return child1, child2

def _mutate(chromosome: List[Job], mutation_rate: float) -> List[Job]:
    """Applies a simple swap mutation to a chromosome."""
    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(len(chromosome)), 2)
        chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
    return chromosome

def optimize_genetic(jobs: List[Job], machine_schedules: Dict[str, MachineSchedule]):
    """
    Main genetic algorithm function.
    Operates on domain objects.
    """
    # GA Parameters
    POPULATION_SIZE = 100
    NUM_GENERATIONS = 100
    MUTATION_RATE = 0.1
    NUM_PARENTS = 20

    machine_names = list(machine_schedules.keys())

    # Initialization
    population = _initialize_population(POPULATION_SIZE, jobs)
    best_chromosome = None
    best_fitness = -1.0

    # Main GA Loop
    for _ in range(NUM_GENERATIONS):
        fitnesses = [_calculate_fitness(chromo, machine_names) for chromo in population]

        current_best_idx = max(range(len(fitnesses)), key=fitnesses.__getitem__)
        if fitnesses[current_best_idx] > best_fitness:
            best_fitness = fitnesses[current_best_idx]
            best_chromosome = population[current_best_idx]

        parents = _selection(population, fitnesses, NUM_PARENTS)
        
        next_population = [best_chromosome] # Elitism

        while len(next_population) < POPULATION_SIZE:
            p1, p2 = random.sample(parents, 2)
            c1, c2 = _crossover(p1, p2)
            next_population.append(_mutate(c1, MUTATION_RATE))
            if len(next_population) < POPULATION_SIZE:
                next_population.append(_mutate(c2, MUTATION_RATE))
        
        population = next_population

    # Once the best order is found, populate the final machine_schedules object
    final_schedules, unscheduled_count = _assign_chromosome_to_machines(best_chromosome, machine_names)
    
    # Transfer the results to the original machine_schedules objects
    for name, schedule in final_schedules.items():
        machine_schedules[name].jobs = schedule.jobs
        machine_schedules[name].current_time_hours = schedule.current_time_hours
        machine_schedules[name].last_impression_type = schedule.last_impression_type

    return unscheduled_count