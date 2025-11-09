# Models package
from .database import (
    LaptopModel, SparePartModel, OrderModel, 
    WarrantyModel, UserModel, get_db, generate_serial_number
)

__all__ = [
    'LaptopModel', 'SparePartModel', 'OrderModel',
    'WarrantyModel', 'UserModel', 'get_db', 'generate_serial_number'
]