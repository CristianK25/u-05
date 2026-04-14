# app/modules/producto/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.producto.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    """
    Repositorio de Productos.
    Agrega queries específicas del dominio sobre el CRUD base.
    Solo habla con la DB — nunca levanta HTTPException.
    """
    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio de Producto.

        Args:
            session (Session): Sesión activa de base de datos.
        """
        super().__init__(session, Producto)

    def count(self) -> int:
        """
        Cuenta la cantidad total de productos.

        Returns:
            int: Total de registros en la tabla Producto.
        """
        return len(self.session.exec(select(Producto)).all())
