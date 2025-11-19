from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# Collections are named after class names lowercased
# Product -> "product" collection
# Order -> "order" collection

class Product(BaseModel):
    id: Optional[str] = Field(default=None, description="Document ID")
    name: str
    slug: str
    description: str
    price: float
    currency: str = "USD"
    image: Optional[HttpUrl] = None
    tags: List[str] = []
    featured: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class OrderItem(BaseModel):
    product_id: str
    quantity: int = 1
    unit_price: float

class CustomerInfo(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    notes: Optional[str] = None

class Order(BaseModel):
    id: Optional[str] = Field(default=None, description="Document ID")
    items: List[OrderItem]
    total: float
    currency: str = "USD"
    customer: CustomerInfo
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
