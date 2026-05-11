"""Dataclass models for the Brands API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Brand:
    """Represents a single brand item returned by GET /brandsList."""

    id: int
    brand: str


@dataclass
class BrandsListResponse:
    """Top-level response payload for GET /brandsList."""

    brands: List[Brand] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "BrandsListResponse":
        items = data.get("brands", []) or []
        return cls(
            brands=[
                Brand(
                    id=item.get("id"),
                    brand=item.get("brand"),
                )
                for item in items
            ]
        )


@dataclass
class MethodNotSupportedResponse:
    """Payload returned when an unsupported HTTP verb is used on /brandsList."""

    responseCode: int
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> "MethodNotSupportedResponse":
        return cls(
            responseCode=data.get("responseCode"),
            message=data.get("message"),
        )


__all__ = ["Brand", "BrandsListResponse", "MethodNotSupportedResponse"]

