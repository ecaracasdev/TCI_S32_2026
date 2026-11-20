from .autenticacion_router import router as autenticacion_router
from .base_router import base_router
from .incidencias_router import router as incidencias_router
from .maquinas_router import router as maquinas_router
from .pedidos_compra_router import router as pedidos_compra_router
from .reparaciones_router import router as reparaciones_router
from .repuestos_router import router as repuestos_router
from .reservas_router import router as reservas_router
from .stock_router import router as stock_router

routers = [
    base_router, autenticacion_router, maquinas_router, repuestos_router, reservas_router, stock_router,
    incidencias_router, reparaciones_router, pedidos_compra_router,
]
__all__ = ["routers"]
