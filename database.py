from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from typing import Optional

class MongoDBConnection:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDBConnection()

async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(
        os.getenv("MONGODB_URL", ""),
        serverSelectionTimeoutMS=5000  # 5 second timeout
    )
    mongodb.database = mongodb.client.booking_service
    
    # Test connection
    try:
        await mongodb.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()

def get_database():
    """Get database instance"""
    return mongodb.database