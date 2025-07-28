export interface Job {
  orden: number;
  referencia: string;
  tipo_de_impresion: string;
  diametro_de_manga: number;
  metros_requeridos: number;
  velocidad_sugerida_m_min: number;
  nivel_de_criticidad: number;
  tiempo_estimado_horas: number;
  tiempo_de_cambio_horas: number;
  hora_inicio: number;
  hora_fin: number;
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
