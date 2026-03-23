import strawberry
from typing import List, Optional
from strawberry.types import Info
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from app import crud

def get_db_session(): # вспом. ф-ия для получения сессии в резолверах
    return SessionLocal()

@strawberry.type # GraphQL типы
class User:
    id: int
    name: str
    email: str
    
    @strawberry.field
    async def tasks(self, info: Info) -> List["Task"]:
        """Получить задачи пользователя"""
        db = get_db_session()
        try:
            user = crud.get_user(db, self.id)
            if user:
                return [Task(id=t.id, title=t.title, description=t.description, user_id=t.user_id) 
                       for t in user.tasks]
            return []
        finally:
            db.close()

@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str]
    user_id: int
    
    @strawberry.field
    async def user(self, info: Info) -> Optional[User]:
        """Получить пользователя для задачи"""
        db = get_db_session()
        try:
            user = crud.get_user(db, self.user_id)
            if user:
                return User(id=user.id, name=user.name, email=user.email)
            return None
        finally:
            db.close()

# Входные типы для мутаций
@strawberry.input
class CreateUserInput:
    name: str
    email: str

@strawberry.input
class UpdateUserInput:
    name: Optional[str] = None
    email: Optional[str] = None

@strawberry.input
class CreateTaskInput:
    title: str
    description: Optional[str] = None
    user_id: int

@strawberry.input
class UpdateTaskInput:
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[int] = None

@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> List[User]:
        """Получить всех пользователей"""
        db = get_db_session()
        try:
            users = crud.get_users(db)
            return [User(id=u.id, name=u.name, email=u.email) for u in users]
        finally:
            db.close()
    
    @strawberry.field
    async def user(self, info: Info, id: int) -> Optional[User]:
        """Получить одного пользователя"""
        db = get_db_session()
        try:
            user = crud.get_user(db, id)
            if user:
                return User(id=user.id, name=user.name, email=user.email)
            return None
        finally:
            db.close()
    
    @strawberry.field
    async def tasks(self, info: Info, user_id: Optional[int] = None) -> List[Task]:
        """Получить задачи"""
        db = get_db_session()
        try:
            tasks = crud.get_tasks(db, user_id)
            return [Task(id=t.id, title=t.title, description=t.description, user_id=t.user_id) 
                   for t in tasks]
        finally:
            db.close()
    
    @strawberry.field
    async def task(self, info: Info, id: int) -> Optional[Task]:
        """Получить одну задачу"""
        db = get_db_session()
        try:
            task = crud.get_task(db, id)
            if task:
                return Task(id=task.id, title=task.title, description=task.description, user_id=task.user_id)
            return None
        finally:
            db.close()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> Optional[User]:
        """Создать пользователя"""
        db = get_db_session()
        try:
            from app.models import UserCreate
            user_create = UserCreate(name=input.name, email=input.email)
            user = crud.create_user(db, user_create)
            if user:
                return User(id=user.id, name=user.name, email=user.email)
            return None
        except ValueError:
            return None
        finally:
            db.close()
    
    @strawberry.mutation
    async def update_user(self, id: int, input: UpdateUserInput) -> Optional[User]:
        """Обновить пользователя"""
        db = get_db_session()
        try:
            from app.models import UserUpdate
            user_update = UserUpdate(name=input.name, email=input.email)
            user = crud.update_user(db, id, user_update)
            if user:
                return User(id=user.id, name=user.name, email=user.email)
            return None
        except ValueError:
            return None
        finally:
            db.close()
    
    @strawberry.mutation
    async def delete_user(self, id: int) -> bool:
        """Удалить пользователя"""
        db = get_db_session()
        try:
            return crud.delete_user(db, id)
        finally:
            db.close()
    
    @strawberry.mutation
    async def create_task(self, input: CreateTaskInput) -> Optional[Task]:
        """Создать задачу"""
        db = get_db_session()
        try:
            from app.models import TaskCreate
            task_create = TaskCreate(
                title=input.title,
                description=input.description,
                user_id=input.user_id
            )
            task = crud.create_task(db, task_create)
            if task:
                return Task(id=task.id, title=task.title, description=task.description, user_id=task.user_id)
            return None
        finally:
            db.close()
    
    @strawberry.mutation
    async def update_task(self, id: int, input: UpdateTaskInput) -> Optional[Task]:
        """Обновить задачу"""
        db = get_db_session()
        try:
            from app.models import TaskUpdate
            task_update = TaskUpdate(
                title=input.title,
                description=input.description,
                user_id=input.user_id
            )
            task = crud.update_task(db, id, task_update)
            if task:
                return Task(id=task.id, title=task.title, description=task.description, user_id=task.user_id)
            return None
        finally:
            db.close()
    
    @strawberry.mutation
    async def delete_task(self, id: int) -> bool:
        """Удалить задачу"""
        db = get_db_session()
        try:
            return crud.delete_task(db, id)
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)