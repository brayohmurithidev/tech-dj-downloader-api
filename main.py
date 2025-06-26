from fastapi import FastAPI
from routers.youtube_download import router as download_router
from routers.auth import router as auth_router
from routers.spotify import router as spotify_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8081",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(download_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(spotify_router, prefix="/api")



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
