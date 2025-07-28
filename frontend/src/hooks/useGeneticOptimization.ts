import { useState, useEffect } from 'react';
import { Schedule, OriginalSummary, OptimizationSummary } from '../types/api';
import { uploadFile, loadLastOptimization, recalculateSchedule } from '../services/apiService';

export const useGeneticOptimization = () => {
  const [file, setFile] = useState<File | null>(null);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [excelSummary, setExcelSummary] = useState<OriginalSummary | null>(null); // Summary from original Excel data
  const [optimizationSummary, setOptimizationSummary] = useState<OptimizationSummary | null>(null); // Summary from optimization/recalculation
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadLoading, setIsLoadLoading] = useState(false);
  const [isRecalculating, setIsRecalculating] = useState(false);

  const calculateExcelSummary = (scheduleData: Schedule | null) => {
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
    setExcelSummary(calculateExcelSummary(schedule));
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
    setExcelSummary(null);
    setOptimizationSummary(null);

    try {
      const response = await uploadFile(file, '/upload-ga/');
      setSchedule(response.optimized_schedule);
      setOptimizationSummary(response.summary);
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
    setExcelSummary(null);
    setOptimizationSummary(null);

    try {
      const scheduleData = await loadLastOptimization('Genetic');
      setSchedule(scheduleData);
      // Note: loadLastOptimization does not return a full OptimizationSummary from backend
      // A basic summary could be calculated here if needed for display
    } catch (err: any) {
      setError(`Error loading last optimization: ${err.message}`);
    } finally {
      setIsLoadLoading(false);
    }
  };

  const recalculateScheduleTimes = async () => {
    if (!schedule) return;

    setIsRecalculating(true);
    setError(null);

    try {
      const response = await recalculateSchedule(schedule);
      setSchedule(response.optimized_schedule);
      setOptimizationSummary(response.summary);
    } catch (err: any) {
      setError(`Error recalculating schedule: ${err.message}`);
    } finally {
      setIsRecalculating(false);
    }
  };

  const handleMoveJob = async (
    machineName: string,
    jobIndex: number,
    direction: "up" | "down"
  ) => {
    if (!schedule) return;

    const updatedSchedule = { ...schedule };
    const machineSchedule = [...updatedSchedule[machineName]];

    const newIndex = direction === "up" ? jobIndex - 1 : jobIndex + 1;

    if (newIndex >= 0 && newIndex < machineSchedule.length) {
      const [movedJob] = machineSchedule.splice(jobIndex, 1);
      machineSchedule.splice(newIndex, 0, movedJob);
      updatedSchedule[machineName] = machineSchedule;
      await setSchedule(updatedSchedule);
      // await recalculateScheduleTimes(); // Call recalculate after state update
    }
  };

  const handleOrderChange = (
    machineName: string,
    jobIndex: number,
    newOrder: number
  ) => {
    if (!schedule) return;

    const updatedSchedule = { ...schedule };
    const machineSchedule = [...updatedSchedule[machineName]];

    // Ensure newOrder is within valid bounds (1-based index)
    const targetIndex = Math.max(
      0,
      Math.min(newOrder - 1, machineSchedule.length - 1)
    );

    if (jobIndex === targetIndex) return; // No change needed

    const [movedJob] = machineSchedule.splice(jobIndex, 1);
    machineSchedule.splice(targetIndex, 0, movedJob);

    updatedSchedule[machineName] = machineSchedule;
    setSchedule(updatedSchedule);
    // recalculateScheduleTimes(); // Call recalculate after state update
  };

  return {
    file,
    schedule,
    setSchedule, // Expose setSchedule for reordering
    excelSummary,
    optimizationSummary,
    error,
    isLoading,
    isLoadLoading,
    isRecalculating,
    handleFileChange,
    handleUpload,
    handleLoadLastOptimization,
    recalculateScheduleTimes,
    handleMoveJob,
    handleOrderChange,
  };
};