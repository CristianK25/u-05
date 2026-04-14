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
    Capa de lógica de negocio para Orden.
    Acá ocurre la magia del cálculo del total y validación con los productos.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_or_404(self, uow: OrdenUnitOfWork, orden_id: int) -> Orden:
        """Helper para buscar una orden o dar 404"""
        orden = uow.ordenes.get_by_id(orden_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con id={orden_id} no encontrada",
            )
        return orden

    def create(self, data: OrdenCreate) -> OrdenPublic:
        """
        Crea una orden completa.
        Flujo de Negocio:
          1. Verifica que los productos enviados existan.
          2. Trae el precio actual del producto y lo "congela" en la orden.
          3. Calcula los subtotales y el TOTAL general de la orden.
          4. Guarda todo (Orden y OrdenItems) en una única transacción.
        """
        with OrdenUnitOfWork(self._session) as uow:
            nueva_orden = Orden(user_email=data.user_email, total_amount=0.0)
            
            # Lista donde iremos acumulando los ítems listos para guardar en BD
            lista_items = []
            monto_total = 0.0
            
            # Recorremos lo que mandó el cliente
            for item_in in data.items:
                # ¡Magia Cross-Module! El UoW de órdenes llama al Repositorio de Productos
                producto_db = uow.productos.get_by_id(item_in.product_id)
                
                # Si algún graciosillo pasa un ID que no existe, todo se suspende.
                if not producto_db:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Producto no encontrado", # Tal cual te lo exigía el JSON
                    )
                
                # Armamos el ítem sellando el precio de "HOY"
                nuevo_item = OrdenItem(
                    product_id=producto_db.id,
                    quantity=item_in.quantity,
                    unit_price=producto_db.price,
                )
                
                # Incrementamos la cuenta total
                monto_total += (producto_db.price * item_in.quantity)
                
                lista_items.append(nuevo_item)
            
            # Le asignamos la lista y el precio calculado a nuestro objeto final de Base de Datos
            nueva_orden.items = lista_items
            nueva_orden.total_amount = monto_total
            
            # Mandamos todo al Repositorio de Órdenes
            uow.ordenes.add(nueva_orden)
            
            # Serializamos la salida al DTO BÁSICO (el que mostrás nomás se crea)
            result = OrdenPublic.model_validate(nueva_orden)

        return result

    def get_by_id(self, orden_id: int) -> OrdenReadWithItems:
        """
        Devuelve el detalle gigante (ANIDADO) de una orden y sus ítems completos.
        Aprovecha la funcionalidad SQLModel de obtener data en el contexto de UOW ("Lazy Loading").
        """
        with OrdenUnitOfWork(self._session) as uow:
            orden = self._get_or_404(uow, orden_id)
            
            # Renderizamos la orden DENTRO de base model para forzar la inyección
            # de los productos anidados (ya que el Schema "OrdenReadWithItems" exige objetos "Producto")
            result = OrdenReadWithItems.model_validate(orden)
            
        return result

    def get_all(self, offset: int = 0, limit: int = 20) -> OrdenList:
        """
        Devuelve la lista paginada de Órdenes con ítems.
        """
        with OrdenUnitOfWork(self._session) as uow:
            ordenes = uow.ordenes.get_all(offset=offset, limit=limit)
            total = uow.ordenes.count()
            
            # Validamos con OrdenReadWithItems para que el JSON se despliegue masivo y anidado
            result = OrdenList(
                data=[OrdenReadWithItems.model_validate(o) for o in ordenes],
                total=total,
            )
        return result
