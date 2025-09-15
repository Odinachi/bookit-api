from fastapi import FastAPI
import uvicorn
from routers import user_router, booking_router

app = FastAPI(
    title="Booking Service API",
    description="A service booking and management system",
    version="1.0.0"
)

# Include routers
app.include_router(user_router.router)
app.include_router(booking_router.router)

@app.get("/")
async def root():
    return {"message": "Booking Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)