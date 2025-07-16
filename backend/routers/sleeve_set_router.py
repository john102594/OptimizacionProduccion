from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.sleeve_set import SleeveSet, SleeveSetCreate
from ..services.sleeve_set_service import SleeveSetService

router = APIRouter(
    prefix="/sleeve_sets",
    tags=["Sleeve Sets"]
)

@router.post("/", response_model=SleeveSet, summary="Crear un nuevo set de mangas")
def create_new_sleeve_set(sleeve_set: SleeveSetCreate, sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    try:
        new_sleeve_set = sleeve_set_service.create_sleeve_set(sleeve_set.development, sleeve_set.num_sleeves, sleeve_set.status)
        return new_sleeve_set
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{sleeve_set_id}", response_model=SleeveSet, summary="Obtener un set de mangas por ID")
def get_single_sleeve_set(sleeve_set_id: int, sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    sleeve_set = sleeve_set_service.get_sleeve_set(sleeve_set_id)
    if not sleeve_set:
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    return sleeve_set

@router.get("/", response_model=List[SleeveSet], summary="Obtener todos los sets de mangas")
def get_all_sleeve_sets_endpoint(sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    return sleeve_set_service.get_all_sleeve_sets()

@router.put("/{sleeve_set_id}", response_model=SleeveSet, summary="Actualizar un set de mangas existente")
def update_existing_sleeve_set(sleeve_set_id: int, sleeve_set: SleeveSetCreate, sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    updated_sleeve_set = sleeve_set_service.update_sleeve_set(sleeve_set_id, sleeve_set.development, sleeve_set.num_sleeves, sleeve_set.status)
    if not updated_sleeve_set:
        raise HTTPException(status_code=404, detail="Sleeve Set not found or no changes applied")
    return updated_sleeve_set

@router.delete("/{sleeve_set_id}", summary="Eliminar un set de mangas")
def delete_single_sleeve_set(sleeve_set_id: int, sleeve_set_service: SleeveSetService = Depends(SleeveSetService)):
    if not sleeve_set_service.delete_sleeve_set(sleeve_set_id):
        raise HTTPException(status_code=404, detail="Sleeve Set not found")
    return {"message": "Sleeve Set deleted successfully"}
