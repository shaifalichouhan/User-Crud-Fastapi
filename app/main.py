from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user as user_router
from app.routers import product as product_router  
from app.routers import stripe_webhook as stripe_router
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Enable CORS (important for Swagger & frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(stripe_router.router)

# JWT Bearer auth setup for docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API with JWT Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
