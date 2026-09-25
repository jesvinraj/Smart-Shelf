"""Shared enums used across the SmartShelf domain model."""
from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    BILLER = "BILLER"
    CASHIER = "CASHIER"
    STAFF = "STAFF"
    USER = "USER"


class PurchaseStatus(str, Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class SaleStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    OTHER = "OTHER"


class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"
    WASTAGE = "WASTAGE"


class ExpiryStatus(str, Enum):
    OK = "OK"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"


class PromoStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"


class DiscountType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"
    BUY_X_GET_Y = "BUY_X_GET_Y"


class NotificationType(str, Enum):
    NEAR_EXPIRY = "NEAR_EXPIRY"
    EXPIRED = "EXPIRED"
    LOW_STOCK = "LOW_STOCK"
    HIGH_RISK = "HIGH_RISK"
    SYSTEM = "SYSTEM"


class WastageReason(str, Enum):
    EXPIRED = "EXPIRED"
    DAMAGED = "DAMAGED"
    SPOILED = "SPOILED"
    OTHER = "OTHER"
