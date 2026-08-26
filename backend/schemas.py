from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LearnerProfile(BaseModel):
    target_goal: Optional[str] = None
    current_skills: list[str] = []
    budget: Optional[str] = None
    time_commitment: Optional[str] = None
    deadline: Optional[str] = None
    preferences: list[str] = []

class ProfilerResponse(BaseModel):
    profile: LearnerProfile
    follow_up_question: Optional[str] = None
    is_complete: bool = False
