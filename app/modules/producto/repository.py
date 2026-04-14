# app/modules/producto/repository.py
from sqlmodel import Session, select
from app.core.repository import BaseRepository
from app.modules.producto.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    """
    Repositorio de Productos.
    Hereda todo el CRUD básico (get_by_id, get_all, add, delete) del BaseRepository.
    Solo agrega operaciones muy puntuales de este dominio.
    """
    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def count(self) -> int:
        """
        Cuenta la cantidad total de productos. 
        Esto es vital para poder devolver el "total" en la paginación (GET /productos).
        """
        return len(self.session.exec(select(Producto)).all())
