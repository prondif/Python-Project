class Warehouse:
    def __init__(self):
        self.stock = {}

    def add_item(self, name, qty):
        name = name.strip().lower()

        if qty <= 0:
            print("Quantity must be positive")
            return

        self.stock[name] = self.stock.get(name, 0) + qty
        print(f"Added {qty} of {name}")

    def remove_item(self, name, qty):
        name = name.strip().lower()

        if name not in self.stock:
            print("Item not found")
            return False

        if self.stock[name] < qty:
            print("Not enough stock")
            return False

        self.stock[name] -= qty

        if self.stock[name] == 0:
            del self.stock[name]

        print(f"Removed {qty} of {name}")
        return True

    def get_any_item(self):
        if not self.stock:
            return None
        return next(iter(self.stock))

    def has_stock(self):
        return len(self.stock) > 0

    def show_stock(self):
        print("\nWarehouse Stock:")
        if not self.stock:
            print("Empty")
        else:
            for name, qty in self.stock.items():
                print(f"{name}: {qty}")