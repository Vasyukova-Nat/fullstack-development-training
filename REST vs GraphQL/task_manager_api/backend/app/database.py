from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

os.makedirs("data", exist_ok=True) # созд. папку для БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/tasks.db"

engine = create_engine( # Созд. движок SQLAlchemy
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # разреш. исп-е в неск. потоках (асинх)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # будет создавать новые сессии для БД

Base = declarative_base() # Базовый класс для всех моделей 

def get_db(): # получение сессии БД
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserDB(Base):
    """SQLAlchemy модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    tasks = relationship("TaskDB", back_populates="user", cascade="all, delete-orphan") # отношение "один ко многим" с задачами

class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    user = relationship("UserDB", back_populates="tasks") # отношение "многие к одному" с пользователем

def init_db():
    Base.metadata.create_all(bind=engine)
    print("БД инициализирована, все таблицы созданы")