from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import database
# from app.db.database import Base, engine, get_db

# Alternative import approach if PYTHONPATH solution doesn't work
# Uncomment this and comment out the above import if needed
from app.db.database import Base, engine, get_db

# Create FastAPI app
app = FastAPI(
    title="XAAM API",
    description="API for the Xpress AI Agent Marketplace",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Include routers
from app.api.routes import tasks, agents, judges, blockchain, encryption, deliverables, wallets

app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(judges.router, prefix="/api/judges", tags=["Judges"])
app.include_router(blockchain.router, prefix="/api/blockchain", tags=["Blockchain"])
app.include_router(encryption.router, prefix="/api/encryption", tags=["Encryption"])
app.include_router(deliverables.router, prefix="/api/deliverables", tags=["Deliverables"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["Wallets"])

# Protocol compliance check
def check_protocol_compliance():
    """
    Check if the developer has acknowledged reading the XAAM protocol whitepaper.
    This is a safeguard to ensure all implementations adhere to the protocol specification.
    """
    whitepaper_read = os.getenv("XAAM_WHITEPAPER_READ", "").lower() == "true"
    
    if not whitepaper_read:
        warning_message = """
        ╔════════════════════════════════════════════════════════════════════════════╗
        ║                               WARNING                                      ║
        ║                                                                            ║
        ║  You MUST read the XAAM Protocol Whitepaper before proceeding with         ║
        ║  implementation. The whitepaper contains the definitive protocol           ║
        ║  specification that all implementations must adhere to.                    ║
        ║                                                                            ║
        ║  To acknowledge that you have read and understood the whitepaper,          ║
        ║  set the XAAM_WHITEPAPER_READ environment variable to "true".              ║
        ║                                                                            ║
        ║  Example:                                                                  ║
        ║    export XAAM_WHITEPAPER_READ=true                                        ║
        ║                                                                            ║
        ║  The whitepaper can be found at: XAAM_Whitepaper.md                        ║
        ╚════════════════════════════════════════════════════════════════════════════╝
        """
        logger.warning(warning_message)
        print(warning_message, file=sys.stderr)
        
        # In development mode, we'll just show a warning
        # In production, you might want to raise an exception or exit
        if os.getenv("ENVIRONMENT", "development") == "production":
            raise RuntimeError("XAAM Protocol Whitepaper must be read before running in production")
    else:
        logger.info("XAAM Protocol Whitepaper compliance check passed")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting XAAM API")
    
    # Check protocol compliance
    check_protocol_compliance()
    
    # Create database tables if they don't exist
    # In production, you would use Alembic migrations instead
    # This is just for development convenience
    try:
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)  # Uncomment to reset database
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down XAAM API")
    # Close database connections
    await engine.dispose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)