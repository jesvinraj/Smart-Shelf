"""Central import point for all models so metadata is complete."""
from data.models.alert import AuditLog, Notification
from data.models.batch import StockBatch
from data.models.discount import Promotion
from data.models.enums import (
    DiscountType,
    ExpiryStatus,
    MovementType,
    NotificationType,
    PaymentMethod,
    PromoStatus,
    PurchaseStatus,
    Role,
    SaleStatus,
    WastageReason,
)
from data.models.inventory import InventoryMovement, Location, LocationTransfer
from data.models.login import LoginLog
from data.models.product import Brand, Category, Product
from data.models.sales import (
    Customer,
    Payment,
    PurchaseOrder,
    PurchaseOrderItem,
    Sale,
    SaleItem,
)
from data.models.supplier import Supplier
from data.models.user import User
from data.models.waste import Wastage

__all__ = [
    "AuditLog",
    "Brand",
    "Category",
    "Customer",
    "DiscountType",
    "ExpiryStatus",
    "InventoryMovement",
    "Location",
    "LocationTransfer",
    "LoginLog",
    "MovementType",
    "Notification",
    "NotificationType",
    "Payment",
    "PaymentMethod",
    "Product",
    "PromoStatus",
    "Promotion",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "PurchaseStatus",
    "Role",
    "Sale",
    "SaleItem",
    "SaleStatus",
    "StockBatch",
    "Supplier",
    "User",
    "Wastage",
    "WastageReason",
]
