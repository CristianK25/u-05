# app/modules/orden/unit_of_work.py
from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.orden.repository import OrdenRepository, OrdenItemRepository
from app.modules.producto.repository import ProductoRepository

class OrdenUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo orden.
    Este es el más importante. Expone tres repositorios que van a compartir 
    la misma ventana de transacción (misma Session de la Base de Datos).
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.ordenes = OrdenRepository(session)
        self.orden_items = OrdenItemRepository(session)
        
        # IMPORTANTE: Metemos el repositorio de Productos acá adentro (Operación Cross-Module)
        # Al armar la OrdenItem necesitamos validar que el Producto exista
        # y agarrar su precio verdadero directamente desde la base de datos (y capaz restar stock si hubiera).
        self.productos = ProductoRepository(session)
