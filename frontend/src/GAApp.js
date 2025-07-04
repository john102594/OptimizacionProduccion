import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState } from 'react';
import axios from 'axios';

function GAApp() {
  const [file, setFile] = useState(null);
  const [schedule, setSchedule] = useState(null);
  const [originalSummary, setOriginalSummary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setIsLoading(true); // Activar el estado de carga
    setError(null); // Limpiar errores previos
    setSchedule(null); // Limpiar resultados previos
    setOriginalSummary(null); // Limpiar resumen previo

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload-ga/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSchedule(response.data.optimized_schedule);
      setOriginalSummary(response.data.original_summary);
    } catch (error) {
      setError('Error uploading file: ' + error.message);
    } finally {
      setIsLoading(false); // Desactivar el estado de carga al finalizar
    }
  };

  return (
    <div className="container mt-5">
      <h1 className="mb-4">Production Schedule Optimizer (Algoritmo Genético)</h1>
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Upload Excel File</h5>
          <div className="mb-3">
            <input className="form-control" type="file" onChange={handleFileChange} accept=".xlsx, .xls" />
          </div>
          <button className="btn btn-primary" onClick={handleUpload} disabled={isLoading}>
            {isLoading ? (
              <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            ) : (
              'Optimize Schedule'
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

      {schedule && Object.keys(schedule).length > 0 && originalSummary && (
        <div className="mt-5">
          <h2>Optimized Schedule per Machine</h2>
          <div className="card mb-4">
            <div className="card-body">
              <h5 className="card-title">Global Schedule Summary (From Excel)</h5>
              <table className="table table-bordered table-sm">
                <thead>
                  <tr>
                    <th>Machine</th>
                    <th>Number of References</th>
                    <th>Total Meters</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(originalSummary).map(([machine, summary]) => (
                    <tr key={machine}>
                      <td>{machine}</td>
                      <td>{summary.num_references}</td>
                      <td>{summary.total_meters}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          {Object.entries(schedule).map(([machine, machineSchedule]) => (
            <div key={machine} className="mb-5">
              <h4>Machine: {machine}</h4>
              {machineSchedule.length > 0 ? (
                <>
                  <table className="table table-bordered">
                  <thead>
                    <tr>
                      {Object.keys(machineSchedule[0]).map((key) => (
                        <th key={key}>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</th>
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
                      <td colSpan={Object.keys(machineSchedule[0]).length - 1}><strong>Total Metros:</strong></td>
                      <td><strong>{machineSchedule.reduce((sum, job) => sum + job.metros_requeridos, 0)}</strong></td>
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
          No schedule could be generated. All tasks exceed the 24-hour limit for all machines.
        </div>
      )}
    </div>
  );
}

export default GAApp;