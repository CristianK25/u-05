# app/modules/producto/schemas.py
#
# Schemas Pydantic de entrada y salida para el módulo producto.
# Separados del modelo de tabla para respetar el principio de
# responsabilidad única: models.py define la DB, schemas.py define
# los contratos HTTP.
from typing import Optional, List
from sqlmodel import SQLModel, Field


# ── Entrada ───────────────────────────────────────────────────────────────────

class ProductoCreate(SQLModel):
    """Body para POST /products/"""
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(ge=0.0)


class ProductoUpdate(SQLModel):
    """Body para PATCH /products/{id} — todos los campos opcionales."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    price: Optional[float] = Field(default=None, ge=0.0)


# ── Salida ────────────────────────────────────────────────────────────────────

class ProductoPublic(SQLModel):
    """Response model: campos que se exponen al cliente."""
    id: int
    name: str
    price: float


class ProductoList(SQLModel):
    """Response model paginado para GET /products/"""
    data: List[ProductoPublic]
    total: int
