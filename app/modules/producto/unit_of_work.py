from sqlmodel import Session
from app.core.unit_of_work import UnitOfWork
from app.modules.producto.repository import ProductoRepository


class ProductoUnitOfWork(UnitOfWork):
    """
    UoW específico del módulo producto.
    Expone los repositorios que el servicio necesita coordinar.

    Al entrar al contexto (with uow:) todos los repositorios
    comparten la misma Session → misma transacción.
    """

    def __init__(self, session: Session) -> None:
        """
        UnitOfWork específico del dominio Producto.

        Extiende el UnitOfWork base y registra los repositorios necesarios
        para operar dentro de una misma transacción consistente.

        Repositorios expuestos:
            - productos: acceso a operaciones sobre Producto

        Args:
            session (Session): Sesión activa de base de datos compartida
                               por todos los repositorios.

        Responsabilidad:
            - Garantizar que todas las operaciones sobre Producto
              se ejecuten dentro de la misma transacción
            - Centralizar commit() y rollback() (heredado del UoW base)

        Uso típico:

            with ProductoUnitOfWork(session) as uow:
                producto = Producto(...)
                uow.productos.add(producto)
        """
        super().__init__(session)
        self.productos = ProductoRepository(session)
