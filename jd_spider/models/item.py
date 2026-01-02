from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Item:
    title: str
    image_url: str
    price_desc: str
    price: float
    comment_count: int
    product_url: str
    shop_name: str
    shop_url: str
    crawl_time: Optional[datetime] = field(default_factory=datetime.now) 