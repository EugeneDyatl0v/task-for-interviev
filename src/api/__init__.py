from src.api.auth.views import router as auth_router
from src.api.collection.views import router as collection_router
from src.api.link.views import router as link_router
from src.api.password_recovery.views import password_recovery_router
from src.api.registration import *  # noqa: F401, E401, E402
from src.api.registration.views import registration_router
from src.api.helpers.app import (
    init_exc_handlers, init_middleware
)

from fastapi import FastAPI


app = FastAPI(
    title="Auth0"
)

init_middleware(app)

app.include_router(auth_router)
app.include_router(collection_router)
app.include_router(link_router)
app.include_router(registration_router)
app.include_router(password_recovery_router)

init_exc_handlers(app)
