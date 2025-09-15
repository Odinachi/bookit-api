from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from routers import user_router, booking_router, service_router, review_router
from database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await connect_to_mongo()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("📝 Running without database - some features may not work")
    
    yield
    
    # Shutdown
    try:
        await close_mongo_connection()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"⚠️  Error closing database connection: {e}")

app = FastAPI(
    title="Booking Service API",
    description="A service booking and management system",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(user_router.router)
app.include_router(service_router.router)
app.include_router(booking_router.router)
app.include_router(review_router.router)

@app.get("/")
async def root():
    return {"message": "Booking Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2000)