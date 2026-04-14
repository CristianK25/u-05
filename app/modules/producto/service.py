# app/modules/producto/service.py
from fastapi import HTTPException, status
from sqlmodel import Session

from app.modules.producto.models import Producto
from app.modules.producto.schemas import ProductoCreate, ProductoPublic, ProductoList
from app.modules.producto.unit_of_work import ProductoUnitOfWork


class ProductoService:
    """
    Capa de lógica de negocio para Producto.
    Acá se realizan todas las operaciones sobre los productos sin tocar
    la base de datos de manera explícita (para eso usa el UoW).
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        """Helper privado para levantar el error 404 si el producto no existe."""
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado",
            )
        return producto

    def create(self, data: ProductoCreate) -> ProductoPublic:
        """Crea un nuevo producto en el sistema."""
        with ProductoUnitOfWork(self._session) as uow:
            # Transformamos el Schema de entrada al Model de base de datos
            producto = Producto.model_validate(data)
            
            # Lo persistimos (hace flush, obtiene su ID generado)
            uow.productos.add(producto)
            
            # Formateamos al Schema de salida DENTRO del with para evitar errores de expiración ORM
            result = ProductoPublic.model_validate(producto)
            
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoList:
        """Devuelve el listado de productos con paginación incluyendo el total."""
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.get_all(offset=offset, limit=limit)
            total = uow.productos.count()
            
            result = ProductoList(
                data=[ProductoPublic.model_validate(p) for p in productos],
                total=total,
            )
        return result

    def get_by_id(self, producto_id: int) -> ProductoPublic:
        """Recupera un solo producto y lo devuelve."""
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoPublic.model_validate(producto)
            
        return result
