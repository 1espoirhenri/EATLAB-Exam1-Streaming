from fastapi import FastAPI
from app.streaming import router as streaming_router

app = FastAPI()

app.include_router(streaming_router)

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="web", html=True), name="web")
