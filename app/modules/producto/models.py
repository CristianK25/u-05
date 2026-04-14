# app/modules/producto/models.py
#
# Contiene SOLO el modelo de tabla SQLModel (Producto).
# Los schemas Pydantic de entrada/salida viven en schemas.py.
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.orden.models import OrdenItem


class Producto(SQLModel, table=True):
    """Tabla productos en la base de datos."""

    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(ge=0.0)

    orden_items: List["OrdenItem"] = Relationship(back_populates="producto")
