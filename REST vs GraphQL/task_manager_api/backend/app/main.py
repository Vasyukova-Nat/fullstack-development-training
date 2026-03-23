from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager
from app.rest.endpoints import router as rest_router
from app.graphql.schema import schema
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI): # инициализация при запуске
    init_db()
    yield

app = FastAPI( # Созд. экземпляр FastAPI
    title="Task Manager API",
    description="API для управления пользователями и задачами с поддержкой REST и GraphQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware( # Настройка CORS
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest_router) # Подключаем REST роутер

graphql_app = GraphQLRouter(schema) # Подключаем GraphQL
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "Task Manager API with SQLite",
        "rest_docs": "/docs",
        "graphql_playground": "/graphql"
    }