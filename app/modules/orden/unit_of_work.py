from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.orden.repository import OrdenRepository, OrdenItemRepository
from app.modules.producto.repository import ProductoRepository


class OrdenUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo orden.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
        UnitOfWork específico del dominio Orden.

        Extiende el UnitOfWork base y registra los repositorios necesarios
        para operar dentro de una misma transacción consistente.

        Repositorios expuestos:
            - ordenes: acceso a operaciones sobre Orden
            - orden_items: acceso a operaciones sobre OrdenItem
            - productos: acceso a operaciones sobre Producto (usado para
                         validaciones de integridad y obtención de precios
                         antes de persistir ítems de orden)

        Args:
            session (Session): Sesión activa de base de datos compartida
                               por todos los repositorios.

        Responsabilidad:
            - Garantizar que todas las operaciones (Orden, OrdenItem, Producto)
              se ejecuten dentro de la misma transacción
            - Centralizar commit() y rollback() (heredado del UoW base)
            - Coordinar múltiples repositorios bajo una única unidad de trabajo

        Uso típico:

            with OrdenUnitOfWork(session) as uow:
                producto = uow.productos.get_by_id(product_id)
                orden = Orden(...)
                uow.ordenes.add(orden)
        """
        super().__init__(session)
        self.ordenes = OrdenRepository(session)
        self.orden_items = OrdenItemRepository(session)
        self.productos = ProductoRepository(session)
