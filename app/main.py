from fastapi import FastAPI
from app.routers import routers

app = FastAPI()

# Include the PDF router with all the endpoints.
app.include_router(routers.router)

@app.get("/")
def read_root():
    return {"Hello": "World!"}
