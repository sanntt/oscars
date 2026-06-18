from fastapi import FastAPI

from oscars.api.routers import vehicles


def create_app() -> FastAPI:
    application = FastAPI(title="Oscars Vehicle API")
    application.include_router(vehicles.router)
    return application


app = create_app()
