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

router = APIRouter()


def get_orden_service(session: Session = Depends(get_session)) -> OrdenService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return OrdenService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=OrdenPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una orden",
)
def create_orden(
    data: OrdenCreate,
    svc: OrdenService = Depends(get_orden_service),
) -> OrdenPublic:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)


@router.get(
    "/",
    response_model=OrdenList,
    summary="Listar órdenes (paginado)",
)
def list_ordenes(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: OrdenService = Depends(get_orden_service),
) -> OrdenList:
    return svc.get_all(offset=offset, limit=limit)


@router.get(
    "/{orden_id}",
    response_model=OrdenReadWithItems,
    summary="Obtener orden por ID con productos anidados",
)
def get_orden(
    orden_id: int,
    svc: OrdenService = Depends(get_orden_service),
) -> OrdenReadWithItems:
    return svc.get_by_id(orden_id)
