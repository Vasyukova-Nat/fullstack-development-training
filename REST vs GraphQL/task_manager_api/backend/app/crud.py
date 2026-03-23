from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import UserDB, TaskDB
from app.models import UserCreate, UserUpdate, TaskCreate, TaskUpdate

def get_user(db: Session, user_id: int) -> Optional[UserDB]:
    """Получить пользователя по ID"""
    return db.query(UserDB).filter(UserDB.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """Получить пользователя по email"""
    return db.query(UserDB).filter(UserDB.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserDB]:
    """Получить список пользователей"""
    return db.query(UserDB).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> UserDB:
    """Создать нового пользователя"""
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError(f"User with email {user.email} already exists")
    
    db_user = UserDB(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Обновляем объект, чтобы получить id
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserDB]:
    """Обновить пользователя"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    if user_update.name is not None: # Обновляем только переданные поля
        db_user.name = user_update.name
    if user_update.email is not None:
        if user_update.email != db_user.email:
            existing = get_user_by_email(db, user_update.email)
            if existing and existing.id != user_id:
                raise ValueError(f"User with email {user_update.email} already exists")
        db_user.email = user_update.email
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Удалить пользователя (задачи удалятся автоматически с cascade)"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

def get_task(db: Session, task_id: int) -> Optional[TaskDB]:
    """Получить задачу по ID"""
    return db.query(TaskDB).filter(TaskDB.id == task_id).first()

def get_tasks(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[TaskDB]:
    """Получить список задач, опционально фильтруя по user_id"""
    query = db.query(TaskDB)
    if user_id is not None:
        query = query.filter(TaskDB.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, task: TaskCreate) -> Optional[TaskDB]:
    """Создать новую задачу"""
    user = get_user(db, task.user_id)
    if not user:
        return None
    
    db_task = TaskDB(
        title=task.title,
        description=task.description,
        user_id=task.user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[TaskDB]:
    """Обновить задачу"""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.user_id is not None:
        user = get_user(db, task_update.user_id)
        if not user:
            return None
        db_task.user_id = task_update.user_id
    
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    """Удалить задачу"""
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True

def get_user_with_tasks(db: Session, user_id: int) -> Optional[dict]:
    """Получить пользователя с его задачами"""
    user = get_user(db, user_id)
    if not user:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "tasks": user.tasks
    }