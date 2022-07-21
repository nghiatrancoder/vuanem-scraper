from dataclasses import dataclass

@dataclass
class ProductVariant:
    size: str
    depth: str
    price: str
    sale_price: str

@dataclass
class Product:
    name: str
    url: str
    images: list[str]
    variants: list[ProductVariant]
