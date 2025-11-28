# In main.py lifespan - REPLACE THE MOCK SETUP:

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- [STARTUP] Initializing Sovereign SQLite ---")
    
    # Remove mock initialization
    # initialize_mock_db()  # DELETE THIS LINE
    
    # Setup SQLite persistence
    await setup_db_pool()
    
    print("--- [LIFESPAN] Sovereign Database Ready ---")
    yield
    print("--- [SHUTDOWN] Closing Sovereign Connections ---")
    await shutdown_db_pool()