from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Exersice_Response(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    user_id: Optional[int] = None
    training_session_id: Optional[int] = None
    class Config:
        from_attributes = True

class Exercise_Create(BaseModel):
    name: str
    sets: int
    reps: int
    weight: float
    class Config:
        from_attributes = True

class TrainingSession_Response(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    date: Optional[datetime] = None
    user_id: Optional[int] = None
    exercises: List[Exersice_Response] = []
    class Config:
        from_attributes = True

class TrainingSession_Response_Simple(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    date: Optional[datetime] = None
    user_id: Optional[int] = None
    class Config:
        from_attributes = True

class TrainingSession_Create(BaseModel):
    type: str
    date: datetime
    class Config:
        from_attributes = True

class User_Response(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True
    training_sessions: List[TrainingSession_Response_Simple] = []
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