import React from "react";
import { Job } from "../../types/api";
import { useGeneticOptimization } from "../../hooks/useGeneticOptimization";

const GAApp: React.FC = () => {
  const {
    schedule,
    setSchedule,
    excelSummary,
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
  } = useGeneticOptimization();

  const getCriticalityColor = (level: number) => {
    if (level >= 5) return "red";
    if (level === 4) return "yellow";
    if (level === 3) return "green";
    if (level === 2) return "gray";
    if (level === 1) return "black";
    return "transparent"; // Default or unknown
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
            disabled={isLoading || isLoadLoading || isRecalculating}
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
            className="btn btn-secondary me-2"
            onClick={handleLoadLastOptimization}
            disabled={isLoading || isLoadLoading || isRecalculating}
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
          {schedule && Object.keys(schedule).length > 0 && (
            <button
              className="btn btn-info"
              onClick={recalculateScheduleTimes}
              disabled={isLoading || isLoadLoading || isRecalculating}
            >
              {isRecalculating ? (
                <span
                  className="spinner-border spinner-border-sm"
                  role="status"
                  aria-hidden="true"
                ></span>
              ) : (
                "Recalculate Times"
              )}
            </button>
          )}
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

      {isRecalculating && (
        <div className="alert alert-info mt-4" role="alert">
          Recalculating times... Please wait.
        </div>
      )}

      {schedule && Object.keys(schedule).length > 0 && (
        <div className="mt-5">
          <h2>Optimized Schedule per Machine</h2>
          {excelSummary && (
            <div className="card mb-4">
              <div className="card-body">
                <h5 className="card-title">Global Schedule Summary</h5>
                <table className="table table-bordered table-sm">
                  <thead>
                    <tr>
                      <th>Machine</th>
                      <th>Number of References</th>
                      <th>Total Meters</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(excelSummary)
                      .sort(([machineA], [machineB]) =>
                        machineA.localeCompare(machineB)
                      )
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
                        {Object.values(excelSummary).reduce(
                          (sum, summary) => sum + summary.num_references,
                          0
                        )}
                      </th>
                      <th>
                        {Object.values(excelSummary).reduce(
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
                          <th>Secuencia</th>
                          {Object.keys(machineSchedule[0])
                            .filter(
                              (key) =>
                                key !== "orden" && key !== "nivel_de_criticidad"
                            ) // Exclude 'orden' and 'nivel_de_criticidad'
                            .map((key) => (
                              <th key={key}>
                                {key
                                  .replace(/_/g, " ")
                                  .replace(/\b\w/g, (l) => l.toUpperCase())}
                              </th>
                            ))}
                          <th>Nivel de Criticidad</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {machineSchedule.map((row: Job, index: number) => (
                          <tr key={index}>
                            <td>
                              <input
                                type="number"
                                className="form-control form-control-sm"
                                value={row.orden}
                                onChange={(e) => {
                                  const newOrderValue = parseInt(
                                    e.target.value
                                  );
                                  if (!isNaN(newOrderValue)) {
                                    const updatedSchedule = { ...schedule };
                                    const machineSchedule = [
                                      ...updatedSchedule[machine],
                                    ];
                                    console.log(machineSchedule);
                                    machineSchedule[index] = {
                                      ...machineSchedule[index],
                                      orden: newOrderValue,
                                    };
                                    updatedSchedule[machine] = machineSchedule;
                                    setSchedule(updatedSchedule);
                                  }
                                }}
                                onBlur={(e) =>
                                  handleOrderChange(
                                    machine,
                                    index,
                                    parseInt(e.target.value)
                                  )
                                }
                                min="1"
                                max={machineSchedule.length}
                                style={{ width: "70px" }}
                              />
                            </td>
                            {Object.entries(row)
                              .filter(
                                ([key]) =>
                                  key !== "orden" &&
                                  key !== "nivel_de_criticidad"
                              )
                              .map(([key, value], i) => (
                                <td key={i}>
                                  {[
                                    "diametro_de_manga",
                                    "metros_requeridos",
                                    "velocidad_sugerida_m_min",
                                  ].includes(key)
                                    ? Math.round(Number(value))
                                    : typeof value === "number"
                                    ? value.toFixed(2)
                                    : value}
                                </td>
                              ))}
                            <td>
                              <div
                                className="criticality-indicator"
                                style={{
                                  backgroundColor: getCriticalityColor(
                                    row.nivel_de_criticidad
                                  ),
                                }}
                              >
                                {row.nivel_de_criticidad}
                              </div>
                            </td>
                            <td>
                              <div
                                className="btn-group"
                                role="group"
                                aria-label="Move job"
                              >
                                <button
                                  className="btn btn-outline-secondary btn-sm"
                                  onClick={() =>
                                    handleMoveJob(machine, index, "up")
                                  }
                                  disabled={index === 0}
                                >
                                  &#9650; {/* Up arrow */}
                                </button>
                                <button
                                  className="btn btn-outline-secondary btn-sm"
                                  onClick={() =>
                                    handleMoveJob(machine, index, "down")
                                  }
                                  disabled={
                                    index === machineSchedule.length - 1
                                  }
                                >
                                  &#9660; {/* Down arrow */}
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
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
};

export default GAApp;
