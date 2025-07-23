from fastapi import FastAPI
from app.routers import user as user_router
from app.routers import product as product_router  

app = FastAPI()


app.include_router(user_router.router)
app.include_router(product_router.router)
