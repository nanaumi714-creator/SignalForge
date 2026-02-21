"""Main entry point for SignalForge FastAPI application."""

import logging
from fastapi import FastAPI
from api import runs, pins, commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SignalForge SCOUT API",
    description="Market research engine for global creators.",
    version="1.0.0"
)

# Register Routers
app.include_router(runs.router)
app.include_router(pins.router)
app.include_router(commands.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "app": "SignalForge SCOUT API",
        "status": "online",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
