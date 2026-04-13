# app/modules/producto/models.py
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Para evitar importación circular, solo importamos OrderItem
# durante la revisión de tipos (TYPE_CHECKING)
if TYPE_CHECKING:
    from app.modules.orden.models import OrdenItem


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(ge=0.0)

    # Relación: Un producto puede estar en muchos OrdenItems
    # el back_populates debe coincidir con el nombre de la variable en OrdenItem
    orden_items: List["OrdenItem"] = Relationship(back_populates="producto")
