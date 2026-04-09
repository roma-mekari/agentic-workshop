"""Route definitions for the PokeProxy service."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/v1")


@router.get("/pokemon/{name_or_id}")
async def get_pokemon(name_or_id: str, request: Request):
    """Proxy GET /pokemon/{name_or_id} to PokeAPI."""
    client = request.app.state.http_client
    response = await client.get(f"/pokemon/{name_or_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Pokemon '{name_or_id}' not found.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Upstream PokeAPI error.")
    return response.json()


@router.get("/pokemon")
async def list_pokemon(request: Request, limit: int = 20, offset: int = 0):
    """Proxy GET /pokemon with pagination to PokeAPI."""
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100.")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0.")
    client = request.app.state.http_client
    response = await client.get("/pokemon", params={"limit": limit, "offset": offset})
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Upstream PokeAPI error.")
    return response.json()


@router.get("/type/{name_or_id}")
async def get_type(name_or_id: str, request: Request):
    """Proxy GET /type/{name_or_id} to PokeAPI."""
    client = request.app.state.http_client
    response = await client.get(f"/type/{name_or_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Type '{name_or_id}' not found.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Upstream PokeAPI error.")
    return response.json()
