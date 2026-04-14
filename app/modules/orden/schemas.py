# app/modules/orden/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo orden.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
from typing import List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from app.modules.producto.schemas import ProductoPublic


# ── Entrada ───────────────────────────────────────────────────────────────────

class OrdenItemCreate(SQLModel):
    """Estructura de un ítem al crear una orden."""
    product_id: int
    quantity: int = Field(gt=0, description="La cantidad debe ser mayor a 0")


class OrdenCreate(SQLModel):
    """Body para POST /orders/"""
    user_email: str
    items: List[OrdenItemCreate]


# ── Salida ────────────────────────────────────────────────────────────────────

class OrdenItemPublic(SQLModel):
    """Response model de ítem al crear la orden (solo IDs y precios)."""
    product_id: int
    quantity: int
    unit_price: float


class OrdenPublic(SQLModel):
    """Response model para POST /orders/ (creación)."""
    id: int
    user_email: str
    total_amount: float
    items: List[OrdenItemPublic]


# ── Salida anidada ────────────────────────────────────────────────────────────

class OrdenItemWithProduct(BaseModel):
    """
    Response model de ítem para GET /orders/{id}.
    Usa BaseModel puro (no SQLModel) para evitar conflictos del validador
    de SQLModel al anidar instancias Pydantic en la construcción del dict.
    """
    quantity: int
    unit_price: float
    producto: ProductoPublic

    model_config = {"from_attributes": True}


class OrdenReadWithItems(BaseModel):
    """
    Response model detallado para GET /orders/{id}.
    Usa BaseModel puro (no SQLModel) para evitar conflictos del validador
    de SQLModel al anidar instancias Pydantic en la construcción del dict.
    """
    id: int
    user_email: str
    total_amount: float
    items: List[OrdenItemWithProduct] = []

    model_config = {"from_attributes": True}


class OrdenList(BaseModel):
    """Response model paginado para GET /orders/"""
    total: int
    data: List[OrdenReadWithItems]

    model_config = {"from_attributes": True}
