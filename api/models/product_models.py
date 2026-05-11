"""Dataclass models for the Products API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Product:
    """Represents a single product item returned by GET /productsList."""

    id: int
    name: str
    # Optional fields - the live API returns more attributes than the minimal
    # contract; keep them optional so the dataclass tolerates either shape.
    price: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[dict] = None


@dataclass
class MethodNotAllowedResponse:
    """Generic error payload returned when an unsupported HTTP method is used."""

    responseCode: int
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> "MethodNotAllowedResponse":
        return cls(
            responseCode=data.get("responseCode"),
            message=data.get("message"),
        )


@dataclass
class ProductsListResponse:
    """Top-level response payload for GET /productsList."""

    products: List[Product] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ProductsListResponse":
        items = data.get("products", []) or []
        return cls(
            products=[
                Product(
                    id=item.get("id"),
                    name=item.get("name"),
                    price=item.get("price"),
                    brand=item.get("brand"),
                    category=item.get("category"),
                )
                for item in items
            ]
        )


__all__ = ["Product", "ProductsListResponse", "MethodNotAllowedResponse"]

