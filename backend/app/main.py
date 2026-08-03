from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, comparisons, fighters, predict
from app.core.config import settings

settings.validate_security()

app = FastAPI(title="UFC Fight Outcome Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, tags=["predict"])
app.include_router(fighters.router, tags=["fighters"])
app.include_router(auth.router, tags=["auth"])
app.include_router(comparisons.router, tags=["comparisons"])


@app.get("/health")
def health():
    return {"status": "ok"}
