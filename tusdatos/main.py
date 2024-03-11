from fastapi import FastAPI

from tusdatos.routers import auth_router, judicial_process_router

app = FastAPI(
    title="TusDatos Technical Test",
    description="Technical test for the position of backend developer for tusdatos.co",
    version="0.1.0",
)
app.include_router(auth_router)
app.include_router(judicial_process_router)
