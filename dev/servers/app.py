from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie

from dev.config import settings
from dev.models.database import get_client
from dev.models.pdf_document import Pdf
from dev.servers.views.pdf_router import router

"""
Este archivo originalmente era main.py, pero no corresponde que sea la entrada del programa,
ni le corresponde el nombre.

Por lo tanto, se movio el entry ponit a /dev y se dejo la logica de flaskAPI que si corresponde.

El nombre app.py era el que sonaba mejor, se puede cambiar.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_client()
    await init_beanie(
        database=client[settings.MONGO_DB_NAME],
        document_models=[Pdf],
    )
    yield
    client.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    return app


app = create_app()
