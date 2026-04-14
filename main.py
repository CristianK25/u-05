from contextlib import asynccontextmanager
from fastapi import FastAPI

# Core
from app.core.database import create_db_and_tables

# Routers de nuestros módulos
from app.modules.producto.router import router as producto_router
from app.modules.orden.router import router as orden_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Controla el ciclo de vida de la aplicación.
    Lo que suceda antes del "yield" pasa al iniciar el servidor (Levantar Base).
    Lo que suceda después, se ejecuta al apagar (Cerrar Conexiones).
    """
    create_db_and_tables()
    yield

# Instanciamos la aplicación FastAPI
app = FastAPI(
    title="API de Órdenes",
    description="Demo de arquitectura Backend con FastAPI, SQLModel, UoW y Repository Pattern",
    version="1.0.0",
    lifespan=lifespan
)

# Conectamos nuestras rutas limpias a la aplicación principal
app.include_router(producto_router)
app.include_router(orden_router)

@app.get("/")
def home():
    return {
        "message": "Bienvenido a la API. Navega hacia /docs para ver y probar todos los endpoints del TP."
    }
