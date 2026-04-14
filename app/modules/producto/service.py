# app/modules/producto/service.py
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.producto.models import Producto
from app.modules.producto.schemas import ProductoCreate, ProductoPublic, ProductoList
from app.modules.producto.unit_of_work import ProductoUnitOfWork


class ProductoService:
    """
    Capa de lógica de negocio para Productos.

    Responsabilidades:
    - Coordinar repositorios a través del UoW
    - Levantar HTTPException cuando corresponde
    - NUNCA acceder directamente a la Session

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
            El servicio no maneja directamente la transacción; delega en ProductoUnitOfWork.
        """
        self._session = session

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        """
        Obtiene un producto por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (ProductoUnitOfWork): Unidad de trabajo activa.
            producto_id (int): ID del producto.

        Returns:
            Producto: Instancia encontrada.

        Raises:
            HTTPException: 404 si el producto no existe.
        """
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    # ── Casos de uso ─────────────────────────────────────────────────────────

    def create(self, data: ProductoCreate) -> ProductoPublic:
        """
        Crea un nuevo producto.

        Flujo:
        - Construye entidad desde DTO
        - Persiste usando repositorio
        - Serializa antes de cerrar la transacción

        Args:
            data (ProductoCreate): Datos de entrada.

        Returns:
            ProductoPublic: DTO de salida.
        """
        with ProductoUnitOfWork(self._session) as uow:
            producto = Producto.model_validate(data)
            uow.productos.add(producto)
            result = ProductoPublic.model_validate(producto)

        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoList:
        """
        Obtiene lista paginada de productos.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            ProductoList: DTO con lista de productos y total.

        Nota:
            El total se calcula con una query separada.
        """
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.get_all(offset=offset, limit=limit)
            total = uow.productos.count()

            result = ProductoList(
                data=[ProductoPublic.model_validate(p) for p in productos],
                total=total,
            )

        return result

    def get_by_id(self, producto_id: int) -> ProductoPublic:
        """
        Obtiene un producto por ID.

        Args:
            producto_id (int): ID del producto.

        Returns:
            ProductoPublic: DTO del producto.

        Raises:
            HTTPException: 404 si no existe.
        """
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoPublic.model_validate(producto)

        return result
