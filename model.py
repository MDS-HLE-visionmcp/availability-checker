from typing import Dict

from pydantic import BaseModel, Field


class CameraDocument(BaseModel):
    id: str = Field(..., alias="_id")
    url: str
    name: str
    description: str
    location: str
    enabled: bool
    available: bool
    metadata: Dict[str, str]