from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import settings, engine
from app.models import Base
from app.api import products, categories, users, orders

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EMC3 Lighting Store API",
    description="MVP Backend для интернет-магазина освещения EMC3",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(
    products.router,
    prefix="/api/products",
    tags=["products"]
)

app.include_router(
    categories.router,
    prefix="/api/categories", 
    tags=["categories"]
)

app.include_router(
    users.router,
    prefix="/api/auth",
    tags=["authentication"]
)

app.include_router(
    orders.router,
    prefix="/api/orders",
    tags=["orders"]
)

@app.get("/")
async def root():
    return {
        "message": "EMC3 Lighting Store API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)