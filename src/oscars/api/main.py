from fastapi import FastAPI

from oscars.api.routers import bookings, vehicles


def create_app() -> FastAPI:
    application = FastAPI(title="Oscars Vehicle API")
    application.include_router(vehicles.router)
    application.include_router(bookings.router)
    return application


app = create_app()
