from fastapi import FastAPI
from app.routers import pdf_router

app = FastAPI()

# Include the PDF router with all the endpoints.
app.include_router(pdf_router.router)

@app.get("/")
def read_root():
    return {"Hello": "World!"}
