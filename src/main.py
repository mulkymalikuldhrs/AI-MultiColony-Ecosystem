from fastapi import FastAPI
from contextlib import asynccontextmanager

# Placeholder for lifespan management (e.g., startup/shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Kilo Backend: System is starting up...")
    yield
    # Code to run on shutdown
    print("Kilo Backend: System is shutting down.")

app = FastAPI(
    title="Mulky AI Colony - Backend Engine",
    description="Unified Backend for AI Agent Management and Task Orchestration.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint to check if the backend is running.
    """
    return {"message": "Kilo Backend is operational."}

# Add routers for agents, tasks, etc.
from src.api.endpoints import agents, tasks

app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)