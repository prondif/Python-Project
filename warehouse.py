class Warehouse:
    """
    Simple Tier 1 warehouse:
    - Tracks items in bulk (name -> quantity)
    """

    def __init__(self):
        # Dictionary to store stock
        # Example: {"apple": 10, "box": 5}
        self.stock = {}

    def add_item(self, name: str, quantity: int) -> None:
        """Add items to warehouse"""
        if quantity <= 0:
            print("Quantity must be positive")
            return

        if name in self.stock:
            self.stock[name] += quantity
        else:
            self.stock[name] = quantity

        print(f"Added {quantity} of {name}")

    def remove_item(self, name: str, quantity: int) -> bool:
        """Remove items from warehouse"""
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

    def get_stock(self) -> dict:
        """Return stock dictionary (useful for testing)"""
        return self.stock

    def show_stock(self) -> None:
        """Print current warehouse stock"""
        print("\nWarehouse Stock:")

        if not self.stock:
            print("Empty")
            return

        for name, qty in self.stock.items():
            print(f"{name}: {qty}")