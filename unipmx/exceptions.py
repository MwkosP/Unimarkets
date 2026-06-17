"""Unified error hierarchy — re-exports pmxt errors with pm aliases."""

from pmxt.errors import (
    AuthError,
    BadRequest,
    InvalidOrder,
    MarketNotFound,
    NotFoundError,
    NotSupported,
    PmxtError,
    RateLimitError,
)

# Spec name — pmxt uses PmxtError as base
UnimarketsError = PmxtError
VenueError = PmxtError

__all__ = [
    "AuthError",
    "BadRequest",
    "InvalidOrder",
    "MarketNotFound",
    "NotFoundError",
    "NotSupported",
    "PmxtError",
    "RateLimitError",
    "UnimarketsError",
    "VenueError",
]
