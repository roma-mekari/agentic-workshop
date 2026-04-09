"""Application entry point."""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from pokeproxy.client import build_client
from pokeproxy.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = build_client()
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="PokeProxy",
    description="A simple proxy service to PokeAPI.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}


def serve():
    uvicorn.run("pokeproxy.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    serve()
