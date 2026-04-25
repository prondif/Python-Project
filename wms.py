class Batch:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

class Warehouse:
    def __init__(self):
        self.batches = []

    def add_batch(self, name, quantity):
        batch = Batch(name, quantity)
        self.batches.append(batch)

    def remove_stock(self, amount):
        while amount > 0 and self.batches:
            first = self.batches[0]

            if first.quantity <= amount:
                amount -= first.quantity
                self.batches.pop(0)
            else:
                first.quantity -= amount
                amount = 0

        if amount > 0:
            print("Not enough stock!")

    def show_stock(self):
        total = 0
        for batch in self.batches:
            print(batch.name, ":", batch.quantity)
            total += batch.quantity

        print("Total stock:", total)

warehouse = Warehouse()

while True:
    print("\n1. Add batch")
    print("2. Remove stock")
    print("3. Show stock")
    print("4. Exit")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Batch name: ")
        qty = int(input("Quantity: "))
        warehouse.add_batch(name, qty)

    elif choice == "2":
        qty = int(input("Amount to remove: "))
        warehouse.remove_stock(qty)

    elif choice == "3":
        warehouse.show_stock()

    elif choice == "4":
        break