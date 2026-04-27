from warehouse import Warehouse

def main():
    warehouse = Warehouse()

    while True:
        print("\n1 - Add item")
        print("2 - Remove item")
        print("3 - Show stock")
        print("9 - Quit")

        sel = int(input("Select: "))

        match sel:
            case 1:
                name = input("Item name: ")
                qty = int(input("Quantity: "))
                warehouse.add_item(name, qty)

            case 2:
                name = input("Item name: ")
                qty = int(input("Quantity: "))
                success = warehouse.remove_item(name, qty)
                if not success:
                    print("Not enough stock!")

            case 3:
                print(warehouse.get_stock())

            case 9:
                break

            case _:
                print("Invalid selection")


if __name__ == "__main__":
    main()