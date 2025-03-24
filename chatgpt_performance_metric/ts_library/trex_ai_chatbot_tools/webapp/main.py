from fastapi import FastAPI
from .routers import monitor, stream
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(monitor.router)
app.include_router(stream.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
