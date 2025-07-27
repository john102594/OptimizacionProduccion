export interface Job {
  id: number;
  nombre: string;
  metros_requeridos: number;
  // Agrega aquí el resto de las propiedades de un 'job'
}

export interface Schedule {
  [machine: string]: Job[];
}

export interface Summary {
  num_references: number;
  total_meters: number;
}

export interface OriginalSummary {
  [machine: string]: Summary;
}

export interface Machine {
  id: number;
  machine_number: string;
  max_material_width: number;
}

export interface SleeveSet {
  id: number;
  development: number;
  num_sleeves: number;
  status: string;
}
