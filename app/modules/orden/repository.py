# app/modules/orden/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.orden.models import Orden, OrdenItem


class OrdenRepository(BaseRepository[Orden]):
    """
    Repositorio de Órdenes.
    Agrega queries específicas del dominio sobre el CRUD base.
    Solo habla con la DB — nunca levanta HTTPException.
    """
    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de Orden.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, Orden)

    def count(self) -> int:
        """
        Cuenta la cantidad total de órdenes.

        Returns:
            int: Total de registros en la tabla Orden.
        """
        return len(self.session.exec(select(Orden)).all())


class OrdenItemRepository(BaseRepository[OrdenItem]):
    """
    Repositorio de OrdenItems (tabla intermedia).
    Solo habla con la DB — nunca levanta HTTPException.
    """
    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de OrdenItem.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, OrdenItem)
