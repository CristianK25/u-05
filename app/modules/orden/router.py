# app/modules/orden/router.py
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.orden.schemas import (
    OrdenCreate,
    OrdenPublic,
    OrdenList,
    OrdenReadWithItems,
)
from app.modules.orden.service import OrdenService

router = APIRouter(prefix="/orders", tags=["Orders"])

# Inyección de dependencia limpia
def get_orden_service(session: Session = Depends(get_session)) -> OrdenService:
    return OrdenService(session)

@router.post("/", response_model=OrdenPublic, status_code=status.HTTP_201_CREATED)
def create_orden(
    data: OrdenCreate,
    service: OrdenService = Depends(get_orden_service)
):
    """
    Crea una orden completa recibiendo los items.
    Toda la validación y cálculo de precios ocurre en el Service.
    """
    return service.create(data)

@router.get("/", response_model=OrdenList)
def read_ordenes(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    service: OrdenService = Depends(get_orden_service)
):
    """Devuelve el listado paginado de órdenes"""
    return service.get_all(offset=offset, limit=limit)

@router.get("/{orden_id}", response_model=OrdenReadWithItems)
def read_orden(
    orden_id: int,
    service: OrdenService = Depends(get_orden_service)
):
    """Devuelve el detalle de la orden anidando los productos enteros"""
    return service.get_by_id(orden_id)
