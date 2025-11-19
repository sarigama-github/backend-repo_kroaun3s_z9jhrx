from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from schemas import Product, Order
from database import create_document, get_documents

app = FastAPI(title="Grid Tech API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str
    price: float
    currency: str = "USD"
    image: str | None = None
    tags: List[str] = []
    featured: bool = False

class OrderCreate(BaseModel):
    items: List[dict]
    total: float
    currency: str = "USD"
    customer: dict

@app.get("/test")
async def test():
    # simple db read to ensure connection works
    try:
        _ = await get_documents("product", {}, 1)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/products", response_model=List[Product])
async def list_products():
    docs = await get_documents("product", {}, 100)
    # normalize
    products = []
    for d in docs:
        products.append(Product(**{
            "id": str(d.get("_id")),
            "name": d.get("name"),
            "slug": d.get("slug"),
            "description": d.get("description"),
            "price": float(d.get("price", 0)),
            "currency": d.get("currency", "USD"),
            "image": d.get("image"),
            "tags": d.get("tags", []),
            "featured": d.get("featured", False),
            "created_at": d.get("created_at"),
            "updated_at": d.get("updated_at"),
        }))
    return products

@app.post("/products", response_model=Product)
async def create_product(payload: ProductCreate):
    doc = await create_document("product", payload.dict())
    return Product(**{
        "id": str(doc.get("_id")),
        **payload.dict(),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    })

@app.post("/orders", response_model=Order)
async def create_order(payload: OrderCreate):
    # basic validation that items exist
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items provided")
    doc = await create_document("order", payload.dict())
    return Order(**{
        "id": str(doc.get("_id")),
        **payload.dict(),
        "status": "pending",
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    })
