from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.transcribe import router as transcribe_router

app = FastAPI(title="Cebuano ASR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router)


@app.get("/")
async def root():
    return {"service": "Cebuano ASR API", "version": "1.0.0"}
