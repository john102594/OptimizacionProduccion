import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

function AppContent() {
  const [file, setFile] = useState(null);
  const [schedule, setSchedule] = useState(null);
  const [originalSummary, setOriginalSummary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadLoading, setIsLoadLoading] = useState(false);

  // Function to calculate summary from schedule
  const calculateSummary = (scheduleData) => {
    const summary = {};
    if (scheduleData) {
      Object.entries(scheduleData).forEach(([machine, machineSchedule]) => {
        let numReferences = 0;
        let totalMeters = 0;
        machineSchedule.forEach(job => {
          numReferences += 1;
          totalMeters += job.metros_requeridos;
        });
        summary[machine] = {
          num_references: numReferences,
          total_meters: totalMeters
        };
      });
    }
    return summary;
  };

  // Effect to update summary whenever schedule changes
  useEffect(() => {
    setOriginalSummary(calculateSummary(schedule));
  }, [schedule]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setIsLoading(true); // Activar el estado de carga
    setError(null); // Limpiar errores previos
    setSchedule(null); // Limpiar resultados previos
    setOriginalSummary(null); // Limpiar resumen previo

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://localhost:8000/upload/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setSchedule(response.data.optimized_schedule);
      console.log("Optimized Schedule received:", response.data.optimized_schedule);
    } catch (error) {
      setError("Error uploading file: " + error.message);
    } finally {
      setIsLoading(false); // Desactivar el estado de carga al finalizar
    }
  };

  const handleLoadLastOptimization = async () => {
    setIsLoadLoading(true);
    setError(null);
    setSchedule(null);
    setOriginalSummary(null);

    try {
      const response = await axios.get(
        "http://localhost:8000/optimization_results/latest/Greedy"
      );
      if (response.data) {
        setSchedule(JSON.parse(response.data.schedule_details));
        console.log("Loaded Schedule from DB:", JSON.parse(response.data.schedule_details));
        setError(null);
      } else {
        setError("No previous Greedy optimization found.");
      }
    } catch (error) {
      setError("Error loading last optimization: " + error.message);
    } finally {
      setIsLoadLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Upload Excel File</h5>
          <div className="mb-3">
            <input
              className="form-control"
              type="file"
              onChange={handleFileChange}
              accept=".xlsx, .xls"
            />
          </div>
          <button
            className="btn btn-primary me-2"
            onClick={handleUpload}
            disabled={isLoading || isLoadLoading}
          >
            {isLoading ? (
              <span
                className="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>
            ) : (
              "Optimize Schedule"
            )}
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleLoadLastOptimization}
            disabled={isLoading || isLoadLoading}
          >
            {isLoadLoading ? (
              <span
                className="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>
            ) : (
              "Load Last Optimization"
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger mt-4" role="alert">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="alert alert-info mt-4" role="alert">
          Optimizing schedule... Please wait.
        </div>
      )}

      {schedule && Object.keys(schedule).length > 0 && (
        <div className="mt-5">
          <h2>Optimized Schedule per Machine</h2>
          {originalSummary && (
            <div className="card mb-4">
              <div className="card-body">
                <h5 className="card-title">
                  Global Schedule Summary (From Excel)
                </h5>
                <table className="table table-bordered table-sm">
                  <thead>
                    <tr>
                      <th>Machine</th>
                      <th>Number of References</th>
                      <th>Total Meters</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(originalSummary)
                    .sort(([machineA], [machineB]) => machineA.localeCompare(machineB))
                    .map(([machine, summary]) => (
                      <tr key={machine}>
                        <td>{machine}</td>
                        <td>{summary.num_references}</td>
                        <td>{summary.total_meters}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <th>Total</th>
                      <th>
                        {Object.values(originalSummary).reduce(
                          (sum, summary) => sum + summary.num_references,
                          0
                        )}
                      </th>
                      <th>
                        {Object.values(originalSummary).reduce(
                          (sum, summary) => sum + summary.total_meters,
                          0
                        )}
                      </th>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}
          {Object.entries(schedule)
            .sort(([machineA], [machineB]) => machineA.localeCompare(machineB))
            .map(([machine, machineSchedule]) => (
            <div key={machine} className="mb-5">
              <h4>Machine: {machine}</h4>
              {machineSchedule.length > 0 ? (
                <>
                  <table className="table table-bordered">
                    <thead>
                      <tr>
                        {Object.keys(machineSchedule[0]).map((key) => (
                          <th key={key}>
                            {key
                              .replace(/_/g, " ")
                              .replace(/\b\w/g, (l) => l.toUpperCase())}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {machineSchedule.map((row, index) => (
                        <tr key={index}>
                          {Object.values(row).map((value, i) => (
                            <td key={i}>{value}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr>
                        <td
                          colSpan={Object.keys(machineSchedule[0]).length - 1}
                        >
                          <strong>Total Metros:</strong>
                        </td>
                        <td>
                          <strong>
                            {machineSchedule.reduce(
                              (sum, job) => sum + job.metros_requeridos,
                              0
                            )}
                          </strong>
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </>
              ) : (
                <p>No tasks scheduled for this machine.</p>
              )}
            </div>
          ))}
        </div>
      )}

      {schedule && Object.keys(schedule).length === 0 && (
        <div className="alert alert-info mt-4" role="alert">
          No schedule could be generated. All tasks exceed the 24-hour limit for
          all machines.
        </div>
      )}
    </div>
  );
}

export default AppContent;
