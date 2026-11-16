from fastapi import FastAPI

from .api import router


app = FastAPI(
    title="Programación lineal",
    description=(
        "API para resolver problemas de programación lineal con Big M "
        "y simplex revisado usando fracciones exactas."
    ),
    version="1.0.0",
)
app.include_router(router)
