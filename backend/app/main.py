from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers import auth_router, category_router, item_router, room_router, family_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Home Assets Trace API",
    description="Family items tracking system API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(item_router)
app.include_router(room_router)
app.include_router(family_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )


@app.get("/")
def root():
    return {"message": "Home Assets Trace API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
