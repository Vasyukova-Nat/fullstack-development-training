from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import get_db
from app import crud
from app.models import User, UserCreate, UserUpdate, Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/api", tags=["REST API"])

@router.get("/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(db: Session = Depends(get_db)):
    """Получение списка всех пользователей"""
    users = crud.get_users(db)
    return users

@router.get("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получение одного пользователя по ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Создание нового пользователя"""
    try:
        user = crud.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Обновление пользователя"""
    try:
        user = crud.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя"""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/tasks", response_model=List[Task])
async def get_tasks(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Получение списка задач. Можно фильтровать по user_id: /tasks?user_id=1"""
    tasks = crud.get_tasks(db, user_id)
    return tasks

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Получение одной задачи по ID"""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Создание новой задачи"""
    task = crud.create_task(db, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="User not found")
    return task

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """Обновление задачи"""
    task = crud.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удаление задачи"""
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")