from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.core.config import get_settings
from app.schemas import TokenResponse
from app.services.auth import issue_tokens, revoke_refresh_token, rotate_refresh_token, upsert_user
from app.services.steam import build_steam_login_url, fetch_player_summary, verify_openid_response

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.get("/steam/login")
def steam_login() -> RedirectResponse:
    return RedirectResponse(build_steam_login_url(), status_code=status.HTTP_302_FOUND)


@router.get("/steam/callback")
async def steam_callback(request: Request, session: SessionDep) -> RedirectResponse:
    settings = get_settings()
    steam_id = await verify_openid_response(request)
    profile = await fetch_player_summary(steam_id)
    user = upsert_user(session, profile)
    tokens = issue_tokens(session, user)
    redirect_params = urlencode(
        {"access_token": tokens.access_token, "refresh_token": tokens.refresh_token}
    )
    return RedirectResponse(f"{settings.frontend_url}/auth/callback?{redirect_params}")


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshRequest, session: SessionDep) -> TokenResponse:
    try:
        return rotate_refresh_token(session, payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, session: SessionDep) -> None:
    revoke_refresh_token(session, payload.refresh_token)
