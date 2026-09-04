from fastapi import APIRouter, Depends

from auth_utils import KeycloakUser, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", summary="Get the authenticated user")
async def get_authenticated_user(
    user: KeycloakUser = Depends(get_current_user),
) -> dict:
    """Return normalized identity and authorization claims for the caller."""

    return dict(user)
