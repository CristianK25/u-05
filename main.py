from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.modules.producto.router import router as producto_router
from app.modules.orden.router import router as orden_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas en la base de datos al iniciar la aplicación."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="API de Órdenes",
    description="Sistema de compras con FastAPI, SQLModel, UoW y Repository Pattern",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(producto_router, prefix="/products", tags=["Products"])
app.include_router(orden_router, prefix="/orders", tags=["Orders"])


@app.get("/")
def home():
    return {"message": "API de Órdenes activa. Visitar /docs para documentación."}
