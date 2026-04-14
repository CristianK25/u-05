# app/modules/orden/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.orden.models import Orden, OrdenItem


class OrdenRepository(BaseRepository[Orden]):
    """
    Repositorio de Órdenes.
    Maneja exclusivamente las consultas a la tabla "ordenes".
    """
    def __init__(self, session: Session) -> None:
        # Le pasamos explícitamente el modelo Orden al BaseRepository
        super().__init__(session, Orden)

    def count(self) -> int:
        """Cuenta la cantidad total de órdenes para la paginación."""
        return len(self.session.exec(select(Orden)).all())


class OrdenItemRepository(BaseRepository[OrdenItem]):
    """
    Repositorio de OrdenItems (tabla intermedia).
    Es un repositorio de apoyo que usará el UnitOfWork de la Orden
    para ir conectando los productos comprados con su orden correspondiente.
    """
    def __init__(self, session: Session) -> None:
        # Le pasamos el modelo OrdenItem
        super().__init__(session, OrdenItem)
