from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dev.config import settings
from dev.repositories.mongo_pdf_repository import MongoPdfRepository
from dev.repositories.pdf_repository import PdfRepository
from dev.servers.views.pdf_router import router


def create_app(repository: PdfRepository | None = None) -> FastAPI:
    if repository is None:
        repository = MongoPdfRepository()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await repository.initialize()
        yield
        await repository.close()

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
    app.state.pdf_repository = repository
    app.include_router(router)

    return app


app = create_app()
