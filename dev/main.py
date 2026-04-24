from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie

from dev.server.config import settings
from dev.server.models.database import get_client
from dev.models import Pdf


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


def main() -> int:
    """Entry-point principal del programa.

    Llama al CLI para procesar PDFs desde línea de comandos.
    """
    import sys
    from dev.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    import sys

    sys.exit(main())