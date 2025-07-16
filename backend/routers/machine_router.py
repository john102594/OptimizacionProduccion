from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.machine import Machine, MachineCreate
from ..models.sleeve_set import SleeveSet # Added import for SleeveSet
from ..services.machine_service import MachineService
from ..services.sleeve_set_service import SleeveSetService # Needed for compatibility checks

router = APIRouter(
    prefix="/machines",
    tags=["Machines"]
)

@router.post("/", response_model=Machine, summary="Crear una nueva máquina")
def create_new_machine(machine: MachineCreate, machine_service: MachineService = Depends(MachineService)):
    try:
        new_machine = machine_service.create_machine(machine.machine_number, machine.max_material_width)
        return new_machine
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{machine_id}", response_model=Machine, summary="Obtener una máquina por ID")
def get_single_machine(machine_id: int, machine_service: MachineService = Depends(MachineService)):
    machine = machine_service.get_machine(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.get("/", response_model=List[Machine], summary="Obtener todas las máquinas")
def get_all_machines_endpoint(machine_service: MachineService = Depends(MachineService)):
    return machine_service.get_all_machines()

@router.put("/{machine_id}", response_model=Machine, summary="Actualizar una máquina existente")
def update_existing_machine(machine_id: int, machine: MachineCreate, machine_service: MachineService = Depends(MachineService)):
    updated_machine = machine_service.update_machine(machine_id, machine.machine_number, machine.max_material_width)
    if not updated_machine:
        raise HTTPException(status_code=404, detail="Machine not found or no changes applied")
    return updated_machine

@router.delete("/{machine_id}", summary="Eliminar una máquina")
def delete_single_machine(machine_id: int, machine_service: MachineService = Depends(MachineService)):
    if not machine_service.delete_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"message": "Machine deleted successfully"}

@router.post("/{machine_id}/compatible_sleeve_sets/{sleeve_set_id}", summary="Asociar un set de mangas a una máquina")
def add_compatibility(machine_id: int, sleeve_set_id: int, machine_service: MachineService = Depends(MachineService), sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    if not machine_service.get_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    if not sleeve_set_service.get_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    if machine_service.add_machine_sleeve_set_compatibility(machine_id, sleeve_set_id):
        return {"message": "Compatibility added successfully"}
    raise HTTPException(status_code=400, detail="Compatibility already exists or invalid IDs")

@router.delete("/{machine_id}/compatible_sleeve_sets/{sleeve_set_id}", summary="Remover la asociación de un set de mangas a una máquina")
def remove_compatibility(machine_id: int, sleeve_set_id: int, machine_service: MachineService = Depends(MachineService), sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    if not machine_service.get_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    if not sleeve_set_service.get_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    if machine_service.remove_machine_sleeve_set_compatibility(machine_id, sleeve_set_id):
        return {"message": "Compatibility removed successfully"}
    raise HTTPException(status_code=404, detail="Compatibility not found")

@router.get("/{machine_id}/compatible_sleeve_sets/", response_model=List[SleeveSet], summary="Obtener sets de mangas compatibles con una máquina")
def get_compatible_sleeve_sets(machine_id: int, machine_service: MachineService = Depends(MachineService)):
    if not machine_service.get_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine_service.get_compatible_sleeve_sets_for_machine(machine_id)

@router.get("/sleeve_sets/{sleeve_set_id}/compatible_machines/", response_model=List[Machine], summary="Obtener máquinas compatibles con un set de mangas")
def get_compatible_machines(sleeve_set_id: int, machine_service: MachineService = Depends(MachineService), sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    if not sleeve_set_service.get_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    return machine_service.get_compatible_machines_for_sleeve_set(sleeve_set_id)
