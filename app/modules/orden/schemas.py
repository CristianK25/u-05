# app/modules/orden/schemas.py
from typing import List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from app.modules.producto.schemas import ProductoPublic

# ── Entrada ───────────────────────────────────────────────────────────────────

class OrdenItemCreate(SQLModel):
    """Estructura de un ítem al crear una orden"""
    product_id: int
    quantity: int = Field(gt=0, description="La cantidad debe ser mayor a 0")


class OrdenCreate(SQLModel):
    """Body para POST /orders"""
    user_email: str
    items: List[OrdenItemCreate]


# ── Salida ────────────────────────────────────────────────────────────────────

class OrdenItemPublic(SQLModel):
    """Ítem que se devuelve al CREAR la orden (solo IDs y precios)"""
    product_id: int
    quantity: int
    unit_price: float


class OrdenPublic(SQLModel):
    """Response para POST /orders (creación)."""
    id: int
    user_email: str
    total_amount: float
    items: List[OrdenItemPublic]


# ── Salida Avanzada (Anidada) ─────────────────────────────────────────────────

class OrdenItemWithProduct(BaseModel):
    """Ítem detallado que se devuelve al hacer GET /orders/{id}"""
    quantity: int
    unit_price: float
    producto: ProductoPublic  # Relación anidada

    model_config = {"from_attributes": True}


class OrdenReadWithItems(BaseModel):
    """Response detallado para GET /orders/{id} (incluye productos)"""
    id: int
    user_email: str
    total_amount: float
    items: List[OrdenItemWithProduct] = []

    model_config = {"from_attributes": True}


class OrdenList(BaseModel):
    """Response model paginado para GET /orders"""
    total: int
    data: List[OrdenReadWithItems]

    model_config = {"from_attributes": True}
