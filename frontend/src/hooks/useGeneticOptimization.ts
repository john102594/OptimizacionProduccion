import { useState, useEffect } from 'react';
import { Schedule, OriginalSummary } from '../types/api';
import { uploadFile, loadLastOptimization } from '../services/apiService';

export const useGeneticOptimization = () => {
  const [file, setFile] = useState<File | null>(null);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [originalSummary, setOriginalSummary] = useState<OriginalSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadLoading, setIsLoadLoading] = useState(false);

  const calculateSummary = (scheduleData: Schedule | null) => {
    const summary: OriginalSummary = {};
    if (scheduleData) {
      Object.entries(scheduleData).forEach(([machine, machineSchedule]) => {
        let numReferences = 0;
        let totalMeters = 0;
        machineSchedule.forEach((job) => {
          numReferences += 1;
          totalMeters += job.metros_requeridos;
        });
        summary[machine] = {
          num_references: numReferences,
          total_meters: totalMeters,
        };
      });
    }
    return summary;
  };

  useEffect(() => {
    setOriginalSummary(calculateSummary(schedule));
  }, [schedule]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSchedule(null);
    setOriginalSummary(null);

    try {
      const scheduleData = await uploadFile(file, '/upload-ga/');
      setSchedule(scheduleData);
    } catch (err: any) {
      setError(`Error uploading file: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadLastOptimization = async () => {
    setIsLoadLoading(true);
    setError(null);
    setSchedule(null);
    setOriginalSummary(null);

    try {
      const scheduleData = await loadLastOptimization('Genetic');
      setSchedule(scheduleData);
    } catch (err: any) {
      setError(`Error loading last optimization: ${err.message}`);
    } finally {
      setIsLoadLoading(false);
    }
  };

  return {
    file,
    schedule,
    originalSummary,
    error,
    isLoading,
    isLoadLoading,
    handleFileChange,
    handleUpload,
    handleLoadLastOptimization,
  };
};