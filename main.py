class Warehouse:
    def __init__(self):
        self.stock = {}

    def add_item(self, name, quantity):
        if name in self.stock:
            self.stock[name] += quantity
        else:
            self.stock[name] = quantity
    
    def remove_item(self, name, quantity):
        if name in self.stock and self.stock[name] >= quantity:
            self.stock[name] -= quantity
        else:
            print("Not enough stock!")


def main():
    warehouse = Warehouse()

    while True:
        print("\n1. Add item")
        print("2. Remove item")
        print("3. Show stock")
        print("4. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Item name: ")
            try:
                qty = int(input("Quantity: "))
            except ValueError:
                print("Please enter a valid number!")
                continue
            warehouse.add_item(name, qty)

        elif choice == "2":
            name = input("Item name: ")
            try:
                qty = int(input("Quantity: "))
            except ValueError:
                print("Please enter a valid number!")
                continue
            warehouse.remove_item(name, qty)

        elif choice == "3":
            print("\nCurrent Stock:")
            for item, qty in warehouse.stock.items():
                print(item, ":", qty)

        elif choice == "4":
            break

        else:
            print("\n" + "="*30)
            print("❌ Invalid choice, please select 1-4.")
            print("="*30)
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()