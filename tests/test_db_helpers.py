import pytest
from core.database import Database

@pytest.fixture
async def db():
    db_instance = Database("mongodb://localhost:27017/sbmoderation")
    yield db_instance
    await db_instance.client.close()

@pytest.mark.asyncio
async def test_insert_and_find(db):
    test_data = {"_id": 1, "name": "test"}
    await db.get_collection("test_collection").insert_one(test_data)
    
    result = await db.get_collection("test_collection").find_one({"_id": 1})
    assert result["name"] == "test"

@pytest.mark.asyncio
async def test_update(db):
    await db.get_collection("test_collection").update_one({"_id": 1}, {"$set": {"name": "updated_test"}})
    
    result = await db.get_collection("test_collection").find_one({"_id": 1})
    assert result["name"] == "updated_test"

@pytest.mark.asyncio
async def test_delete(db):
    await db.get_collection("test_collection").delete_one({"_id": 1})
    
    result = await db.get_collection("test_collection").find_one({"_id": 1})
    assert result is None