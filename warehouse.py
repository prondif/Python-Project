class Warehouse:
    """
    Simple Tier 1 warehouse:
    - Tracks items in bulk (name -> quantity)
    """

    def __init__(self):
        self.stock = {}

    def add_item(self, name: str, quantity: int) -> None:
        name = name.strip().lower()

        if quantity <= 0:
            print("Quantity must be positive")
            return

        self.stock[name] = self.stock.get(name, 0) + quantity
        print(f"Added {quantity} of {name}")

    def remove_item(self, name: str, quantity: int) -> bool:
        name = name.strip().lower()

        if quantity <= 0:
            print("Quantity must be positive")
            return False

        if name not in self.stock:
            print("Item not found")
            return False

        if self.stock[name] < quantity:
            print("Not enough stock")
            return False

        self.stock[name] -= quantity

        if self.stock[name] == 0:
            del self.stock[name]

        print(f"Removed {quantity} of {name}")
        return True

    def has_stock(self) -> bool:
        """Check if any stock exists"""
        return len(self.stock) > 0

    def get_any_item(self):
        """Get one item name for auto transfer"""
        if not self.stock:
            return None
        return next(iter(self.stock))

    def show_stock(self) -> None:
        print("\nWarehouse Stock:")

        if not self.stock:
            print("Empty")
            return

        for name, qty in self.stock.items():
            print(f"{name}: {qty}")