# app/modules/producto/router.py
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.producto.schemas import ProductoCreate, ProductoPublic, ProductoList
from app.modules.producto.service import ProductoService

# Definimos el router con su prefijo
router = APIRouter(prefix="/products", tags=["Products"])

# Inyector de dependencias: El router no sabe qué es una Session, 
# se la pasa transparente al Service para respetar el comentario del Database.
def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    return ProductoService(session)

@router.post("/", response_model=ProductoPublic, status_code=status.HTTP_201_CREATED)
def create_producto(
    data: ProductoCreate,
    service: ProductoService = Depends(get_producto_service),
):
    """Crea un nuevo producto"""
    # El router NO TIENE LÓGICA. Solo patea la pelota al Service.
    return service.create(data)

@router.get("/", response_model=ProductoList)
def read_productos(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    service: ProductoService = Depends(get_producto_service),
):
    """Devuelve listado paginado de productos"""
    return service.get_all(offset=offset, limit=limit)

@router.get("/{producto_id}", response_model=ProductoPublic)
def read_producto(
    producto_id: int,
    service: ProductoService = Depends(get_producto_service),
):
    """Trae el detalle de un producto particular"""
    return service.get_by_id(producto_id)
