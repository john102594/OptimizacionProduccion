import { useState, useEffect } from 'react';
import { Machine, SleeveSet } from '../types/api';
import * as api from '../services/apiService';

export const useManagement = () => {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [sleeveSets, setSleeveSets] = useState<SleeveSet[]>([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMachines();
    fetchSleeveSets();
  }, []);

  const fetchMachines = async () => {
    try {
      const data = await api.getMachines();
      setMachines(data);
    } catch (err: any) {
      setError(`Error fetching machines: ${err.message}`);
    }
  };

  const fetchSleeveSets = async () => {
    try {
      const data = await api.getSleeveSets();
      setSleeveSets(data);
    } catch (err: any) {
      setError(`Error fetching sleeve sets: ${err.message}`);
    }
  };

  const handleAddMachine = async (machine: Omit<Machine, 'id'>) => {
    try {
      await api.addMachine(machine);
      setMessage('Machine added successfully!');
      fetchMachines();
    } catch (err: any) {
      setError(`Error adding machine: ${err.message}`);
    }
  };

  const handleUpdateMachine = async (id: number, machine: Omit<Machine, 'id'>) => {
    try {
      await api.updateMachine(id, machine);
      setMessage('Machine updated successfully!');
      fetchMachines();
    } catch (err: any) {
      setError(`Error updating machine: ${err.message}`);
    }
  };

  const handleDeleteMachine = async (id: number) => {
    try {
      await api.deleteMachine(id);
      setMessage('Machine deleted successfully!');
      fetchMachines();
    } catch (err: any) {
      setError(`Error deleting machine: ${err.message}`);
    }
  };

  const handleAddSleeveSet = async (sleeveSet: Omit<SleeveSet, 'id'>) => {
    try {
      await api.addSleeveSet(sleeveSet);
      setMessage('Sleeve Set added successfully!');
      fetchSleeveSets();
    } catch (err: any) {
      setError(`Error adding sleeve set: ${err.message}`);
    }
  };

  const handleUpdateSleeveSet = async (id: number, sleeveSet: Omit<SleeveSet, 'id'>) => {
    try {
      await api.updateSleeveSet(id, sleeveSet);
      setMessage('Sleeve Set updated successfully!');
      fetchSleeveSets();
    } catch (err: any) {
      setError(`Error updating sleeve set: ${err.message}`);
    }
  };

  const handleDeleteSleeveSet = async (id: number) => {
    try {
      await api.deleteSleeveSet(id);
      setMessage('Sleeve Set deleted successfully!');
      fetchSleeveSets();
    } catch (err: any) {
      setError(`Error deleting sleeve set: ${err.message}`);
    }
  };

  const handleAddCompatibility = async (machineId: number, sleeveSetId: number) => {
    try {
      await api.addCompatibility(machineId, sleeveSetId);
      setMessage('Compatibility added successfully!');
    } catch (err: any) {
      setError(`Error adding compatibility: ${err.message}`);
    }
  };

  return {
    machines,
    sleeveSets,
    message,
    error,
    handleAddMachine,
    handleUpdateMachine,
    handleDeleteMachine,
    handleAddSleeveSet,
    handleUpdateSleeveSet,
    handleDeleteSleeveSet,
    handleAddCompatibility,
  };
};