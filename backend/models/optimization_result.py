from pydantic import BaseModel

class OptimizationResult(BaseModel):
    id: int
    algorithm_type: str
    timestamp: str
    total_time: float
    total_cost: float
    schedule_details: str

    class Config:
        orm_mode = True
