import React from "react";
import { useOptimization } from "../../hooks/useOptimization";
import { Job } from "../../types/api";

const AppContent: React.FC = () => {
  const {
    schedule,
    setSchedule,
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
  } = useOptimization();

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

          {optimizationSummary && (
            <div className="card mb-4">
              <div className="card-body">
                <h5 className="card-title">Optimization Summary</h5>
                <table className="table table-bordered table-sm">
                  <thead>
                    <tr>
                      <th>Total Time (Hours)</th>
                      <th>Unscheduled Jobs</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>{optimizationSummary.total_time.toFixed(2)}</td>
                      <td>{optimizationSummary.unscheduled_jobs}</td>
                    </tr>
                  </tbody>
                </table>
                <h6>Machine Details:</h6>
                <table className="table table-bordered table-sm">
                  <thead>
                    <tr>
                      <th>Machine</th>
                      <th>Total Time (Hours)</th>
                      <th>Total Meters</th>
                      <th>Setup Time (Hours)</th>
                      <th>Number of Jobs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {optimizationSummary.machine_summary.map((ms, index) => (
                      <tr key={index}>
                        <td>{ms.machine}</td>
                        <td>{ms.total_time.toFixed(2)}</td>
                        <td>{ms.total_meters.toFixed(2)}</td>
                        <td>{ms.setup_time.toFixed(2)}</td>
                        <td>{ms.num_jobs}</td>
                      </tr>
                    ))}
                  </tbody>
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
                          <th>Order</th>{" "}
                          {/* New column for direct order input */}
                          <th>Actions</th> {/* New column for buttons */}
                        </tr>
                      </thead>
                      <tbody>
                        {machineSchedule.map((row: Job, index: number) => (
                          <tr key={index}>
                            {Object.entries(row).map(([key, value], i) => (
                              <td key={i}>
                                {typeof value === "number"
                                  ? value.toFixed(2)
                                  : value}
                              </td>
                            ))}
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

export default AppContent;
