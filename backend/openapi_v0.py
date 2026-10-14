"""Aplicación FastAPI exclusiva para generar el borrador del contrato OpenAPI v0."""

from fastapi import FastAPI

from openapi_v0_contract import router


app = FastAPI(
    title="TCI - API de Stock y Mantenimiento",
    version="0.0.0",
    description=(
        "Contrato preliminar v0 derivado de docs/dominio/dominio.md y del esquema "
        "backend/db/main.dbml. Las operaciones son declarativas y todavía no "
        "están conectadas a servicios ni a persistencia."
    ),
    openapi_tags=[
        {"name": "Máquinas", "description": "Consulta y mantenimiento de máquinas y sus tipos."},
        {"name": "Repuestos", "description": "Catálogo, búsqueda y datos generales de repuestos."},
        {"name": "Stock", "description": "Existencias por ubicación, alertas y trazabilidad de movimientos."},
        {"name": "Ubicaciones", "description": "Ubicaciones físicas disponibles para almacenar repuestos."},
        {"name": "Incidencias", "description": "Reporte y consulta de fallas detectadas en máquinas."},
        {"name": "Reparaciones", "description": "Seguimiento de reparaciones, consumos e informes de resolución."},
        {"name": "Pedidos de compra", "description": "Creación y gestión del ciclo de vida de pedidos de compra."},
        {"name": "Recepciones", "description": "Registro de artículos recibidos para un pedido de compra."},
        {"name": "Reservas", "description": "Planificación, liberación y ejecución de reservas de stock."},
        {"name": "Autenticación", "description": "Identidad y permisos del usuario autenticado."},
    ],
    docs_url=None,
    redoc_url=None,
)
app.include_router(router)


_generate_openapi = app.openapi


def _generate_openapi_in_spanish() -> dict:
    """Localiza las descripciones genéricas que FastAPI agrega por defecto."""
    schema = app.openapi_schema or _generate_openapi()
    parameter_metadata = {
        "offset": (
            "Desplazamiento",
            "Cantidad de registros que se omiten antes de comenzar el resultado.",
        ),
        "limit": ("Límite", "Cantidad máxima de resultados por página."),
        "maquina_id": ("Identificador de máquina", "Identificador de la máquina consultada."),
        "repuesto_id": ("Identificador de repuesto", "Identificador del repuesto consultado o usado como filtro."),
        "ubicacion_id": ("Identificador de ubicación", "Identificador de la ubicación usada como filtro."),
        "incidencia_id": ("Identificador de incidencia", "Identificador de la incidencia consultada."),
        "reparacion_id": ("Identificador de reparación", "Identificador de la reparación consultada."),
        "pedido_id": ("Identificador de pedido", "Identificador del pedido de compra consultado."),
        "reserva_id": ("Identificador de reserva", "Identificador de la reserva consultada."),
        "codigo": ("Código", "Código QR o de barras del repuesto."),
        "estado": ("Estado", "Filtra los resultados por estado actual."),
    }

    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            for parameter in operation.get("parameters", []):
                metadata = parameter_metadata.get(parameter.get("name"))
                if metadata is not None:
                    title, description = metadata
                    parameter.setdefault("schema", {})["title"] = title
                    parameter.setdefault("description", description)
            for response in operation.get("responses", {}).values():
                if response.get("description") == "Successful Response":
                    response["description"] = "La operación se completó correctamente."
                elif response.get("description") == "Validation Error":
                    response["description"] = (
                        "Los datos enviados no cumplen el formato esperado."
                    )

    validation_schemas = schema.get("components", {}).get("schemas", {})
    if "HTTPValidationError" in validation_schemas:
        validation_schemas["HTTPValidationError"].update(
            title="Error de validación HTTP",
            description="Errores de validación detectados en la solicitud.",
        )
    if "ValidationError" in validation_schemas:
        validation_schemas["ValidationError"].update(
            title="Detalle del error de validación",
            description="Describe un dato de la solicitud que no superó la validación.",
        )
        property_titles = {
            "loc": "Ubicación del dato",
            "msg": "Mensaje",
            "type": "Tipo de error",
            "input": "Valor recibido",
            "ctx": "Contexto",
        }
        for name, title in property_titles.items():
            property_schema = validation_schemas["ValidationError"].get(
                "properties", {}
            ).get(name)
            if property_schema is not None:
                property_schema["title"] = title

    app.openapi_schema = schema
    return schema


app.openapi = _generate_openapi_in_spanish
