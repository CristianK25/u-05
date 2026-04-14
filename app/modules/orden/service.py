# app/modules/orden/service.py
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.orden.models import Orden, OrdenItem
from app.modules.orden.schemas import (
    OrdenCreate,
    OrdenPublic,
    OrdenList,
    OrdenReadWithItems,
)
from app.modules.orden.unit_of_work import OrdenUnitOfWork


class OrdenService:
    """
    Servicio de aplicación para la entidad Orden.

    Responsabilidades:
    - Orquestar casos de uso relacionados a órdenes
    - Coordinar múltiples repositorios mediante UnitOfWork
    - Validar reglas de negocio a nivel aplicación
    - Levantar HTTPException cuando corresponde
    - NUNCA acceder directamente a la Session

    Características:
    - Soporta operaciones cross-module (Orden + Producto)
    - Mantiene consistencia transaccional usando OrdenUnitOfWork

    REGLA IMPORTANTE — objetos ORM y commit():
    Después de que el UoW hace commit(), SQLAlchemy expira los atributos
    del objeto ORM. Toda serialización (model_dump / model_validate)
    debe ocurrir DENTRO del bloque `with uow:`, antes de que __exit__
    dispare el commit.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el servicio con una sesión de base de datos.

        Args:
            session (Session): Sesión activa que será utilizada por el UnitOfWork.

        Nota:
            El servicio no maneja directamente la transacción; delega en OrdenUnitOfWork.
        """
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: OrdenUnitOfWork, orden_id: int) -> Orden:
        """
        Obtiene una orden por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (OrdenUnitOfWork): Unidad de trabajo activa.
            orden_id (int): ID de la orden.

        Returns:
            Orden: Instancia encontrada.

        Raises:
            HTTPException: 404 si la orden no existe.
        """
        orden = uow.ordenes.get_by_id(orden_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con id={orden_id} no encontrada",
            )
        return orden

    # ── Casos de uso ─────────────────────────────────────────────────────────

    def create(self, data: OrdenCreate) -> OrdenPublic:
        """
        Crea una orden completa con sus ítems.

        Flujo:
        - Itera los ítems recibidos
        - Valida existencia del producto (cross-module)
        - Congela el precio actual del producto en el ítem
        - Calcula subtotales y total general
        - Persiste Orden + OrdenItems en una única transacción

        Args:
            data (OrdenCreate): Datos de entrada con email e ítems.

        Returns:
            OrdenPublic: DTO de la orden creada.

        Raises:
            HTTPException: 404 si algún producto no existe.
        """
        with OrdenUnitOfWork(self._session) as uow:
            nueva_orden = Orden(user_email=data.user_email, total_amount=0.0)

            lista_items = []
            monto_total = 0.0

            for item_in in data.items:
                producto_db = uow.productos.get_by_id(item_in.product_id)

                if not producto_db:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Producto no encontrado",
                    )

                nuevo_item = OrdenItem(
                    product_id=producto_db.id,
                    quantity=item_in.quantity,
                    unit_price=producto_db.price,
                )

                monto_total += producto_db.price * item_in.quantity
                lista_items.append(nuevo_item)

            nueva_orden.items = lista_items
            nueva_orden.total_amount = monto_total

            uow.ordenes.add(nueva_orden)
            result = OrdenPublic.model_validate(nueva_orden)

        return result

    def get_by_id(self, orden_id: int) -> OrdenReadWithItems:
        """
        Obtiene una orden por ID con sus ítems y productos anidados.

        Caso cross-module:
        - Consulta Orden
        - Accede a OrdenItems y Productos relacionados via lazy loading

        Args:
            orden_id (int): ID de la orden.

        Returns:
            OrdenReadWithItems: DTO con datos embebidos.

        Raises:
            HTTPException: 404 si no existe.
        """
        with OrdenUnitOfWork(self._session) as uow:
            orden = self._get_or_404(uow, orden_id)
            result = OrdenReadWithItems.model_validate(orden)

        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> OrdenList:
        """
        Obtiene lista paginada de órdenes con ítems y productos.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            OrdenList: DTO con lista de órdenes y total.

        Nota:
            El total se calcula con una query separada.
        """
        with OrdenUnitOfWork(self._session) as uow:
            ordenes = uow.ordenes.get_all(offset=offset, limit=limit)
            total = uow.ordenes.count()

            result = OrdenList(
                data=[OrdenReadWithItems.model_validate(o) for o in ordenes],
                total=total,
            )

        return result
