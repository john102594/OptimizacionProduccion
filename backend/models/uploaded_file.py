from pydantic import BaseModel

class UploadedFileInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: str
    file_hash: str

    class Config:
        orm_mode = True
