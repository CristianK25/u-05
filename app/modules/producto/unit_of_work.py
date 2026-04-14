# app/modules/producto/unit_of_work.py
from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.producto.repository import ProductoRepository

class ProductoUnitOfWork(UnitOfWork):
    """
    UoW específico para el módulo de Producto.
    Acá adentro metemos únicamente el repositorio de productos, 
    porque al crear un producto (en este caso) no nos interesa saber de órdenes.
    """
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        # Exponemos el repositorio listo para usarse
        self.productos = ProductoRepository(session)
