from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(title="Oscars Vehicle API")


app = create_app()
