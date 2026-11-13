from datetime import UTC, datetime


def fecha_actual() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
