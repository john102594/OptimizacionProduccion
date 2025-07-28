from ..utils.setup_utils import get_setup_time

class Job:
    def __init__(self, job_data: dict):
        self.data = job_data
        self.referencia = job_data['referencia']
        self.metros_requeridos = job_data['metros_requeridos']
        # Handle both 'velocidad_sugerida' (from original df) and 'velocidad_sugerida_m_min' (from frontend)
        self.velocidad_sugerida = job_data.get('velocidad_sugerida_m_min', job_data.get('velocidad_sugerida'))
        self.tipo_de_impresion = job_data['tipo_de_impresion']
        self.nivel_de_criticidad = job_data['nivel_de_criticidad']
        self.maquina_sugerida = job_data.get('maquina_sugerida', None) # Can be None if not explicitly passed
        self.diametro_de_manga = job_data['diametro_de_manga']

        # Correctly get original_index from pandas Series if job_data is a Series
        if hasattr(job_data, 'name'): # Check if it's a pandas Series
            self.original_index = job_data.name
        else: # Assume it's a dict from frontend, original_index might be passed explicitly
            self.original_index = job_data.get('original_index', None)

    def get_duration_hours(self) -> float:
        """Calculates the execution time of the job in hours."""
        if self.velocidad_sugerida > 0:
            return self.metros_requeridos / (self.velocidad_sugerida * 60)
        return float('inf')

class MachineSchedule:
    def __init__(self, machine_name: str):
        self.machine_name = machine_name
        self.jobs = []
        self.current_time_hours = 0.0
        self.last_impression_type = None

    def can_add_job(self, job: Job, setup_time: float) -> bool:
        """Checks if a job can be added within the 24-hour limit."""
        return self.current_time_hours + job.get_duration_hours() + setup_time <= 24

    def add_job(self, job: Job, setup_time: float):
        """Adds a job to the schedule and updates the machine's state."""
        job_duration = job.get_duration_hours()
        
        start_time = self.current_time_hours
        end_time = start_time + job_duration + setup_time

        # Store calculated times within a temporary dictionary in the job list
        self.jobs.append({
            'job_object': job,
            'start_time': round(start_time, 2),
            'end_time': round(end_time, 2),
            'setup_time': round(setup_time, 2),
            'duration': round(job_duration, 2)
        })

        self.current_time_hours = end_time
        self.last_impression_type = job.tipo_de_impresion

    def get_last_impression_type(self) -> str | None:
        return self.last_impression_type

    def get_current_time(self) -> float:
        return self.current_time_hours

    def get_total_meters(self) -> float:
        """Calculates the sum of meters for all jobs in the schedule."""
        return sum(scheduled_item['job_object'].metros_requeridos for scheduled_item in self.jobs)

    def to_dict_list(self) -> list:
        """Converts the schedule into a list of dictionaries for the final JSON response."""
        schedule_list = []
        for i, scheduled_item in enumerate(self.jobs):
            job = scheduled_item['job_object']
            schedule_list.append({
                'orden': i + 1,
                'referencia': job.referencia,
                'tipo_de_impresion': job.tipo_de_impresion,
                'diametro_de_manga': float(job.diametro_de_manga),
                'metros_requeridos': float(job.metros_requeridos),
                'velocidad_sugerida_m_min': float(job.velocidad_sugerida),
                'nivel_de_criticidad': int(job.nivel_de_criticidad),
                'tiempo_estimado_horas': scheduled_item['duration'],
                'tiempo_de_cambio_horas': scheduled_item['setup_time'],
                'hora_inicio': scheduled_item['start_time'],
                'hora_fin': scheduled_item['end_time']
            })
        return schedule_list
