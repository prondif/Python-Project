class Warehouse:
    def __init__(self):
        self.stock = {}

    def add_item(self, name, qty):
        name = name.strip().lower()
        self.stock[name] = self.stock.get(name, 0) + qty
        print(f"Added {qty} of {name}")

    def remove_item(self, name, qty):
        name = name.strip().lower()

        if name not in self.stock or self.stock[name] < qty:
            return False

        self.stock[name] -= qty

        if self.stock[name] == 0:
            del self.stock[name]

        print(f"Removed {qty} of {name}")
        return True

    def has_stock(self):
        return len(self.stock) > 0

    def get_any_item(self):
        if not self.stock:
            return None
        return next(iter(self.stock))