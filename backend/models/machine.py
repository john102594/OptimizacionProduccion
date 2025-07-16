from pydantic import BaseModel

class MachineBase(BaseModel):
    machine_number: str
    max_material_width: float

class MachineCreate(MachineBase):
    pass

class Machine(MachineBase):
    id: int

    class Config:
        orm_mode = True
