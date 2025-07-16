from pydantic import BaseModel

class SleeveSetBase(BaseModel):
    development: int
    num_sleeves: int
    status: str # 'disponible', 'en uso', 'fuera de servicio'

class SleeveSetCreate(SleeveSetBase):
    pass

class SleeveSet(SleeveSetBase):
    id: int

    class Config:
        orm_mode = True
