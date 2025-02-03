from fastapi import FastAPI
 
app = FastAPI()
 
# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
 
# Example endpoint with path parameters
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
 
# Example endpoint with query parameters
@app.get("/search/")
def search(query: str):
    return {"query": query}
 
# POST request with a request body
from pydantic import BaseModel
 
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
 
@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
