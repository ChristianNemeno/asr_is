from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.transcribe import router as transcribe_router
from routes.training import router as training_router
from routes.samples import router as samples_router
from routes.plots import router as plots_router

app = FastAPI(title="Cebuano ASR Training Showcase", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router)
app.include_router(training_router)
app.include_router(samples_router)
app.include_router(plots_router)


@app.get("/")
async def root():
    return {"service": "Cebuano ASR Training Showcase", "version": "2.0.0"}
