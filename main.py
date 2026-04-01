from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GameCrew API", version="1.0")

# Data model for request body validation
class Item(BaseModel):
    name: str
    price: float
    quantity: int

# List
items_db = {}


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "GameCrew API!"}

# Add a new item. 
@app.post("/items/")
def create_item(item: Item):
    item_id = len(items_db) + 1
    items_db[item_id] = item.dict()
    return {"id": item_id, "item": items_db[item_id]}

# Search for an item by ID.
@app.get("/items/{item_id}")
def search_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# Delete an item by ID.
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted_item = items_db.pop(item_id)
    return {"message": "Item deleted", "item": deleted_item}