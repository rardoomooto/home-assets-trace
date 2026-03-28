try:
    from app.models.models import User, Category, Item, Room
    __all__ = ["User", "Category", "Item", "Room"]
except ImportError:
    # Room model may not be defined in this environment yet
    from app.models.models import User, Category, Item
    __all__ = ["User", "Category", "Item"]
