# Gemini Context

This file stores context related to the `production_optimizer` project for the Gemini CLI.

## Project Overview

- **Type:** Production Optimization Application
- **Backend:** Python (FastAPI, likely)
- **Frontend:** React.js (using Create React App, Bootstrap for styling)
- **Data:** Excel files (`datos_produccion.xlsx`, `datos_produccion_grandes.xlsx`)
- **Purpose:** Optimize production schedules, possibly related to scheduling and setup times.

## Frontend Structure and Functionalities

- **Routing:** Uses `react-router-dom` for navigation.
    - **`/` (Greedy Algorithm):** Handled by `frontend/src/components/ui/AppContent.tsx`. Uses `frontend/src/hooks/useOptimization.ts`.
    - **`/ga` (Genetic Algorithm):** Handled by `frontend/src/components/pages/GAApp.tsx`. Uses `frontend/src/hooks/useGeneticOptimization.ts`.
    - **`/management` (Management):** Handled by `frontend/src/components/pages/ManagementPage.tsx`. Uses `frontend/src/hooks/useManagement.ts`.

- **Optimization Pages (`AppContent.tsx` and `GAApp.tsx`):**
    - Allow users to upload Excel files for production schedule optimization.
    - Provide functionality to load the last optimization results.
    - Enable recalculation of schedule times based on current job order.
    - Display a global summary of data from the original Excel file (number of references, total meters).
    - Show an optimization summary (total time, unscheduled jobs, machine-specific details).
    - Allow users to reorder jobs within a machine's schedule using drag-and-drop or direct input.

- **Management Page (`ManagementPage.tsx`):**
    - Provides an interface for managing machine configurations (add, update, delete machine number and max material width).
    - Allows management of sleeve sets (add, update, delete development, number of sleeves, and status).
    - Enables adding compatibility between machines and sleeve sets.

- **API Communication:** All frontend-backend communication is handled by `frontend/src/services/apiService.ts` using `axios`.

- **Data Structures:** TypeScript interfaces for data models (e.g., `Job`, `Schedule`, `Machine`, `SleeveSet`, `OptimizationSummary`, `OriginalSummary`) are defined in `frontend/src/types/api.ts`.

## Recent Activities

- **Fixed:** `Adjacent JSX elements must be wrapped in an enclosing tag` error in `frontend/src/App.js` by wrapping adjacent elements in a React Fragment.
- **Modified Backend (`backend/main.py`):** Added `original_summary` to the API response, containing number of references and total meters from the original Excel file per machine.
- **Modified Frontend (`frontend/src/App.js`):**
    - Removed individual machine summary cards.
    - Added a global summary table at the top, displaying original Excel data (number of references and total meters) per machine.
    - Updated state management to handle `original_summary` from the backend.

## Current Task

- Waiting for user to confirm if the changes to display original Excel data in the global summary table are correct.