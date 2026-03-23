from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Заголовок задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")
    user_id: int = Field(..., description="ID пользователя")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    user_id: Optional[int] = None

class Task(TaskBase):
    id: int = Field(..., description="Уникальный идентификатор задачи")
    class Config:
        from_attributes = True