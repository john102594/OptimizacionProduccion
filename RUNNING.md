# Cómo correr el proyecto Production Optimizer

Este documento describe cómo levantar y correr tanto el backend (FastAPI) como el frontend (React.js) del proyecto Production Optimizer.

## 1. Backend (FastAPI)

El backend está desarrollado en Python utilizando el framework FastAPI.

### Requisitos

*   Python 3.9+
*   pip (administrador de paquetes de Python)

### Pasos para correr el Backend

1.  **Navegar al directorio del backend:**
    ```bash
    cd backend
    ```

2.  **Instalar las dependencias:**
    Asegúrate de tener `pip` instalado. Luego, instala las librerías necesarias listadas en `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Iniciar el servidor FastAPI:**
    Una vez instaladas las dependencias, puedes iniciar el servidor.
    ```bash
    uvicorn main:app --reload
    ```
    El servidor estará disponible por defecto en `http://127.0.0.1:8000`.

## 2. Frontend (React.js)

El frontend está desarrollado en React.js.

### Requisitos

*   Node.js (versión recomendada LTS)
*   npm (administrador de paquetes de Node.js, viene con Node.js)

### Pasos para correr el Frontend

1.  **Navegar al directorio del frontend:**
    ```bash
    cd frontend
    ```

2.  **Instalar las dependencias:**
    Instala las dependencias de Node.js listadas en `package.json`.
    ```bash
    npm install
    ```

3.  **Iniciar la aplicación React:**
    Esto iniciará el servidor de desarrollo de React.
    ```bash
    npm start
    ```
    La aplicación se abrirá automáticamente en tu navegador por defecto, usualmente en `http://localhost:3000`.

---

**Nota:** Asegúrate de que el backend esté corriendo antes de intentar usar la aplicación frontend, ya que el frontend se comunica con el backend para obtener los datos y la lógica de optimización.
