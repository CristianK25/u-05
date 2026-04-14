# app/modules/orden/models.py
#
# Contiene los modelos de tabla SQLModel (Orden y OrdenItem).
# Los schemas Pydantic de entrada/salida viven en schemas.py.
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.producto.models import Producto


class OrdenItem(SQLModel, table=True):
    """Tabla orden_items en la base de datos (tabla intermedia)."""

    __tablename__ = "orden_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0.0)

    order_id: int = Field(foreign_key="ordenes.id")
    product_id: int = Field(foreign_key="productos.id")

    orden: "Orden" = Relationship(back_populates="items")
    producto: "Producto" = Relationship(back_populates="orden_items")


class Orden(SQLModel, table=True):
    """Tabla ordenes en la base de datos."""

    __tablename__ = "ordenes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    total_amount: float = Field(default=0.0, ge=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    items: List["OrdenItem"] = Relationship(back_populates="orden")
