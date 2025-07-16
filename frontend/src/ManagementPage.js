import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function ManagementPage() {
    console.log("ManagementPage loaded");
    
    const [machines, setMachines] = useState([]);
    const [sleeveSets, setSleeveSets] = useState([]);
    const [newMachineNumber, setNewMachineNumber] = useState('');
    const [newMachineWidth, setNewMachineWidth] = useState('');
    const [newSleeveDevelopment, setNewSleeveDevelopment] = useState('');
    const [newSleeveNum, setNewSleeveNum] = useState('');
    const [newSleeveStatus, setNewSleeveStatus] = useState('disponible');
    const [selectedMachineId, setSelectedMachineId] = useState('');
    const [selectedSleeveSetId, setSelectedSleeveSetId] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const [editingMachineId, setEditingMachineId] = useState(null);
    const [editedMachineNumber, setEditedMachineNumber] = useState('');
    const [editedMachineWidth, setEditedMachineWidth] = useState('');

    const [editingSleeveSetId, setEditingSleeveSetId] = useState(null);
    const [editedSleeveDevelopment, setEditedSleeveDevelopment] = useState('');
    const [editedSleeveNum, setEditedSleeveNum] = useState('');
    const [editedSleeveStatus, setEditedSleeveStatus] = useState('');

    useEffect(() => {
        fetchMachines();
        fetchSleeveSets();
    }, []);

    const fetchMachines = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/machines/`);
            setMachines(response.data);
        } catch (err) {
            setError('Error fetching machines: ' + err.message);
        }
    };

    const fetchSleeveSets = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/sleeve_sets/`);
            setSleeveSets(response.data);
        } catch (err) {
            setError('Error fetching sleeve sets: ' + err.message);
        }
    };

    const handleAddMachine = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${API_BASE_URL}/machines/`, {
                machine_number: newMachineNumber,
                max_material_width: parseFloat(newMachineWidth),
            });
            setMessage('Machine added successfully!');
            setNewMachineNumber('');
            setNewMachineWidth('');
            fetchMachines();
        } catch (err) {
            setError('Error adding machine: ' + err.message);
        }
    };

    const handleAddSleeveSet = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${API_BASE_URL}/sleeve_sets/`, {
                development: parseInt(newSleeveDevelopment),
                num_sleeves: parseInt(newSleeveNum),
                status: newSleeveStatus,
            });
            setMessage('Sleeve Set added successfully!');
            setNewSleeveDevelopment('');
            setNewSleeveNum('');
            setNewSleeveStatus('disponible');
            fetchSleeveSets();
        } catch (err) {
            setError('Error adding sleeve set: ' + err.message);
        }
    };

    const handleAddCompatibility = async (e) => {
        e.preventDefault();
        if (!selectedMachineId || !selectedSleeveSetId) {
            setError('Please select both a machine and a sleeve set.');
            return;
        }
        try {
            await axios.post(`${API_BASE_URL}/machines/${selectedMachineId}/compatible_sleeve_sets/${selectedSleeveSetId}`);
            setMessage('Compatibility added successfully!');
            setSelectedMachineId('');
            setSelectedSleeveSetId('');
        } catch (err) {
            setError('Error adding compatibility: ' + err.message);
        }
    };

    const handleDeleteMachine = async (machineId) => {
        try {
            await axios.delete(`${API_BASE_URL}/machines/${machineId}`);
            setMessage('Machine deleted successfully!');
            fetchMachines();
        } catch (err) {
            setError('Error deleting machine: ' + err.message);
        }
    };

    const handleEditMachine = (machine) => {
        setEditingMachineId(machine.id);
        setEditedMachineNumber(machine.machine_number);
        setEditedMachineWidth(machine.max_material_width);
    };

    const handleSaveMachine = async (machineId) => {
        try {
            await axios.put(`${API_BASE_URL}/machines/${machineId}`, {
                machine_number: editedMachineNumber,
                max_material_width: parseFloat(editedMachineWidth),
            });
            setMessage('Machine updated successfully!');
            setEditingMachineId(null);
            fetchMachines();
        } catch (err) {
            setError('Error updating machine: ' + err.message);
        }
    };

    const handleCancelEditMachine = () => {
        setEditingMachineId(null);
    };

    const handleDeleteSleeveSet = async (sleeveSetId) => {
        try {
            await axios.delete(`${API_BASE_URL}/sleeve_sets/${sleeveSetId}`);
            setMessage('Sleeve Set deleted successfully!');
            fetchSleeveSets();
        } catch (err) {
            setError('Error deleting sleeve set: ' + err.message);
        }
    };

    const handleEditSleeveSet = (sleeveSet) => {
        setEditingSleeveSetId(sleeveSet.id);
        setEditedSleeveDevelopment(sleeveSet.development);
        setEditedSleeveNum(sleeveSet.num_sleeves);
        setEditedSleeveStatus(sleeveSet.status);
    };

    const handleSaveSleeveSet = async (sleeveSetId) => {
        try {
            await axios.put(`${API_BASE_URL}/sleeve_sets/${sleeveSetId}`, {
                development: parseInt(editedSleeveDevelopment),
                num_sleeves: parseInt(editedSleeveNum),
                status: editedSleeveStatus,
            });
            setMessage('Sleeve Set updated successfully!');
            setEditingSleeveSetId(null);
            fetchSleeveSets();
        } catch (err) {
            setError('Error updating sleeve set: ' + err);
        }
    };

    const handleCancelEditSleeveSet = () => {
        setEditingSleeveSetId(null);
    };

    return (
        <div className="container mt-5">
            <h1 className="mb-4">Management Page</h1>

            {message && <div className="alert alert-success">{message}</div>}
            {error && <div className="alert alert-danger">{error}</div>}

            <div className="row">
                <div className="col-md-6">
                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Add New Machine</h5>
                            <form onSubmit={handleAddMachine}>
                                <div className="mb-3">
                                    <label htmlFor="machineNumber" className="form-label">Machine Number</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="machineNumber"
                                        value={newMachineNumber}
                                        onChange={(e) => setNewMachineNumber(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="machineWidth" className="form-label">Max Material Width</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        id="machineWidth"
                                        value={newMachineWidth}
                                        onChange={(e) => setNewMachineWidth(e.target.value)}
                                        step="0.01"
                                        required
                                    />
                                </div>
                                <button type="submit" className="btn btn-primary">Add Machine</button>
                            </form>
                        </div>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Add New Sleeve Set</h5>
                            <form onSubmit={handleAddSleeveSet}>
                                <div className="mb-3">
                                    <label htmlFor="sleeveDevelopment" className="form-label">Development</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        id="sleeveDevelopment"
                                        value={newSleeveDevelopment}
                                        onChange={(e) => setNewSleeveDevelopment(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="sleeveNum" className="form-label">Number of Sleeves</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        id="sleeveNum"
                                        value={newSleeveNum}
                                        onChange={(e) => setNewSleeveNum(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="sleeveStatus" className="form-label">Status</label>
                                    <select
                                        className="form-select"
                                        id="sleeveStatus"
                                        value={newSleeveStatus}
                                        onChange={(e) => setNewSleeveStatus(e.target.value)}
                                    >
                                        <option value="disponible">Disponible</option>
                                        <option value="en uso">En Uso</option>
                                        <option value="fuera de servicio">Fuera de Servicio</option>
                                    </select>
                                </div>
                                <button type="submit" className="btn btn-primary">Add Sleeve Set</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <div className="card mb-4">
                <div className="card-body">
                    <h5 className="card-title">Manage Machine-Sleeve Set Compatibility</h5>
                    <form onSubmit={handleAddCompatibility}>
                        <div className="mb-3">
                            <label htmlFor="selectMachine" className="form-label">Select Machine</label>
                            <select
                                className="form-select"
                                id="selectMachine"
                                value={selectedMachineId}
                                onChange={(e) => setSelectedMachineId(e.target.value)}
                                required
                            >
                                <option value="">-- Select a Machine --</option>
                                {machines.map((machine) => (
                                    <option key={machine.id} value={machine.id}>
                                        {machine.machine_number} (Max Width: {machine.max_material_width})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="mb-3">
                            <label htmlFor="selectSleeveSet" className="form-label">Select Sleeve Set</label>
                            <select
                                className="form-select"
                                id="selectSleeveSet"
                                value={selectedSleeveSetId}
                                onChange={(e) => setSelectedSleeveSetId(e.target.value)}
                                required
                            >
                                <option value="">-- Select a Sleeve Set --</option>
                                {sleeveSets.map((sleeveSet) => (
                                    <option key={sleeveSet.id} value={sleeveSet.id}>
                                        Development: {sleeveSet.development}, Sleeves: {sleeveSet.num_sleeves}, Status: {sleeveSet.status}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <button type="submit" className="btn btn-primary">Add Compatibility</button>
                    </form>
                </div>
            </div>

            <div className="row">
                <div className="col-md-6">
                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Existing Machines</h5>
                            {machines.length > 0 ? (
                                <table className="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Machine Number</th>
                                            <th>Max Width</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {machines.map((machine) => (
                                            <tr key={machine.id}>
                                                <td>
                                                    {editingMachineId === machine.id ? (
                                                        <input
                                                            type="text"
                                                            className="form-control"
                                                            value={editedMachineNumber}
                                                            onChange={(e) => setEditedMachineNumber(e.target.value)}
                                                        />
                                                    ) : (
                                                        machine.machine_number
                                                    )}
                                                </td>
                                                <td>
                                                    {editingMachineId === machine.id ? (
                                                        <input
                                                            type="number"
                                                            className="form-control"
                                                            value={editedMachineWidth}
                                                            onChange={(e) => setEditedMachineWidth(e.target.value)}
                                                            step="0.01"
                                                        />
                                                    ) : (
                                                        machine.max_material_width
                                                    )}
                                                </td>
                                                <td>
                                                    {editingMachineId === machine.id ? (
                                                        <>
                                                            <button className="btn btn-sm btn-success me-2" onClick={() => handleSaveMachine(machine.id)}>Save</button>
                                                            <button className="btn btn-sm btn-secondary" onClick={handleCancelEditMachine}>Cancel</button>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <button className="btn btn-sm btn-warning me-2" onClick={() => handleEditMachine(machine)}>Edit</button>
                                                            <button className="btn btn-sm btn-danger" onClick={() => handleDeleteMachine(machine.id)}>Delete</button>
                                                        </>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <p>No machines added yet.</p>
                            )}
                        </div>
                    </div>
                </div>
                <div className="col-md-6">
                    <div className="card mb-4">
                        <div className="card-body">
                            <h5 className="card-title">Existing Sleeve Sets</h5>
                            {sleeveSets.length > 0 ? (
                                <table className="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Development</th>
                                            <th>Number of Sleeves</th>
                                            <th>Status</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {sleeveSets.map((sleeveSet) => (
                                            <tr key={sleeveSet.id}>
                                                <td>
                                                    {editingSleeveSetId === sleeveSet.id ? (
                                                        <input
                                                            type="number"
                                                            className="form-control"
                                                            value={editedSleeveDevelopment}
                                                            onChange={(e) => setEditedSleeveDevelopment(e.target.value)}
                                                        />
                                                    ) : (
                                                        sleeveSet.development
                                                    )}
                                                </td>
                                                <td>
                                                    {editingSleeveSetId === sleeveSet.id ? (
                                                        <input
                                                            type="number"
                                                            className="form-control"
                                                            value={editedSleeveNum}
                                                            onChange={(e) => setEditedSleeveNum(e.target.value)}
                                                        />
                                                    ) : (
                                                        sleeveSet.num_sleeves
                                                    )}
                                                </td>
                                                <td>
                                                    {editingSleeveSetId === sleeveSet.id ? (
                                                        <select
                                                            className="form-select"
                                                            value={editedSleeveStatus}
                                                            onChange={(e) => setEditedSleeveStatus(e.target.value)}
                                                        >
                                                            <option value="disponible">Disponible</option>
                                                            <option value="en uso">En Uso</option>
                                                            <option value="fuera de servicio">Fuera de Servicio</option>
                                                        </select>
                                                    ) : (
                                                        sleeveSet.status
                                                    )}
                                                </td>
                                                <td>
                                                    {editingSleeveSetId === sleeveSet.id ? (
                                                        <>
                                                            <button className="btn btn-sm btn-success me-2" onClick={() => handleSaveSleeveSet(sleeveSet.id)}>Save</button>
                                                            <button className="btn btn-sm btn-secondary" onClick={handleCancelEditSleeveSet}>Cancel</button>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <button className="btn btn-sm btn-warning me-2" onClick={() => handleEditSleeveSet(sleeveSet)}>Edit</button>
                                                            <button className="btn btn-sm btn-danger" onClick={() => handleDeleteSleeveSet(sleeveSet.id)}>Delete</button>
                                                        </>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <p>No sleeve sets added yet.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ManagementPage;
