import axios from 'axios';
import { Schedule, Machine, SleeveSet } from '../types/api';

const API_URL = 'http://localhost:8000';

// Optimization Functions
export const uploadFile = async (file: File, endpoint: string): Promise<Schedule> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_URL}${endpoint}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data.optimized_schedule;
};

export const loadLastOptimization = async (algorithm: string): Promise<Schedule> => {
  const response = await axios.get(`${API_URL}/optimization_results/latest/${algorithm}`);
  if (response.data) {
    return JSON.parse(response.data.schedule_details);
  }
  throw new Error(`No previous ${algorithm} optimization found.`);
};

// Machine Functions
export const getMachines = async (): Promise<Machine[]> => {
  const response = await axios.get(`${API_URL}/machines/`);
  return response.data;
};

export const addMachine = async (machine: Omit<Machine, 'id'>): Promise<Machine> => {
  const response = await axios.post(`${API_URL}/machines/`, machine);
  return response.data;
};

export const updateMachine = async (id: number, machine: Omit<Machine, 'id'>): Promise<Machine> => {
  const response = await axios.put(`${API_URL}/machines/${id}`, machine);
  return response.data;
};

export const deleteMachine = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/machines/${id}`);
};

// SleeveSet Functions
export const getSleeveSets = async (): Promise<SleeveSet[]> => {
  const response = await axios.get(`${API_URL}/sleeve_sets/`);
  return response.data;
};

export const addSleeveSet = async (sleeveSet: Omit<SleeveSet, 'id'>): Promise<SleeveSet> => {
  const response = await axios.post(`${API_URL}/sleeve_sets/`, sleeveSet);
  return response.data;
};

export const updateSleeveSet = async (id: number, sleeveSet: Omit<SleeveSet, 'id'>): Promise<SleeveSet> => {
  const response = await axios.put(`${API_URL}/sleeve_sets/${id}`, sleeveSet);
  return response.data;
};

export const deleteSleeveSet = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/sleeve_sets/${id}`);
};

// Compatibility Functions
export const addCompatibility = async (machineId: number, sleeveSetId: number): Promise<void> => {
  await axios.post(`${API_URL}/machines/${machineId}/compatible_sleeve_sets/${sleeveSetId}`);
};
