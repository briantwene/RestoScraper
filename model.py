from pydantic import BaseModel
from typing import Optional

class RestaurantInfo(BaseModel):
    name: str
    website: str
    location: Optional[str] = None