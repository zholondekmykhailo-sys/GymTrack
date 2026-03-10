from pydantic import BaseModel
from typing import Optional, List


class Exersice_Response(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    user_id: Optional[int] = None
    class Config:
        from_attributes = True

class Exercise_Create(BaseModel):
    name: str
    sets: int
    reps: int
    weight: float
    class Config:
        from_attributes = True

class User_Response(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True
    exercises: List[Exersice_Response] = []
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email:Optional[str] = None