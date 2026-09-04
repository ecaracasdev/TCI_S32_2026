from fastapi import APIRouter


base_router = APIRouter(prefix='/base', tags=["base"])

@base_router.get('')
def base():
    return "OK ROUTER BASE"