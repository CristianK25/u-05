# app/modules/orden/models.py
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

# Evitamos importación circular (solo para tipado)
if TYPE_CHECKING:
    from app.modules.producto.models import Producto


class OrdenItem(SQLModel, table=True):
    __tablename__ = "orden_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0.0)

    # Foreing Keys (Claves Foráneas)
    order_id: int = Field(foreign_key="ordenes.id")
    product_id: int = Field(foreign_key="productos.id")

    # Relaciones inversas (back_populates)
    orden: "Orden" = Relationship(back_populates="items")
    producto: "Producto" = Relationship(back_populates="orden_items")


class Orden(SQLModel, table=True):
    __tablename__ = "ordenes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)  # Indexado para búsquedas rápidas por usuario
    total_amount: float = Field(default=0.0, ge=0.0)
    
    # default_factory para asignar la hora UTC exacta al momento de crear en memoria
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relación: Una Orden tiene muchos OrdenItems
    items: List["OrdenItem"] = Relationship(back_populates="orden")
