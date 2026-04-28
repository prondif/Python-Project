"""Simple interactive ADS tester + Tier 1 Warehouse system"""

from __future__ import annotations

import sys
from time import sleep

try:
    from py_ads_client import ADSClient, ADSSymbol, BOOL, INT, LREAL
except ModuleNotFoundError as exc:
    if exc.name != "py_ads_client":
        raise

    print("Missing dependency: py_ads_client")
    print("Run the tester with the project virtual environment:")
    print(r"  .\.venv\Scripts\python.exe .\simple_interface_tester.py")
    print("If needed, install dependencies first:")
    print(r"  .\.venv\Scripts\python.exe -m pip install -e .[dev]")
    sys.exit(1)


# ---------------- PLC CONNECTION ----------------
PLC_IP = "127.0.0.1"
PLC_NET_ID = "127.0.0.1.1.1"
PLC_PORT = 851
LOCAL_NET_ID = "127.0.0.1.1.2"

CONVEYOR_STATE = ADSSymbol("StatusVars.ConveyorState", INT)
REMOTE_SEND_PALLET = ADSSymbol("Remote.send_pallet", BOOL)
REMOTE_RELEASE_FROM_IMAGING = ADSSymbol("Remote.release_from_imaging", BOOL)
REMOTE_RETURN_PALLET = ADSSymbol("Remote.return_pallet", BOOL)
REMOTE_TRANSFER_ITEM = ADSSymbol("Remote.transfer_item", BOOL)
REMOTE_SRC_X = ADSSymbol("Remote.src_x", LREAL)
REMOTE_SRC_Y = ADSSymbol("Remote.src_y", LREAL)
REMOTE_DST_X = ADSSymbol("Remote.dst_x", LREAL)
REMOTE_DST_Y = ADSSymbol("Remote.dst_y", LREAL)


# ---------------- WAREHOUSE LOGIC ----------------
class Warehouse:
    def __init__(self):
        self.stock = {}

    def add_item(self, name, qty):
        if name in self.stock:
            self.stock[name] += qty
        else:
            self.stock[name] = qty
        print(f"Added {qty} of {name}")

    def remove_item(self, name, qty):
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

    def show_stock(self):
        print("\nWarehouse Stock:")
        if not self.stock:
            print("Empty")
        else:
            for name, qty in self.stock.items():
                print(f"{name}: {qty}")


# ---------------- STATE PRINTING ----------------
def print_state(state: int) -> None:
    match state:
        case 0:
            print("s000_initialize")
        case 1:
            print("s001_not_homed")
        case 10:
            print("s010_homing")
        case 100:
            print("s100_braking")
        case 101:
            print("s101_waiting_at_home")
        case 110:
            print("s110_moving_to_imaging")
        case 120:
            print("s120_imaging")
        case 130:
            print("s130_moving_to_slot")
        case 140:
            print("s140_waiting_in_slot")
        case 150:
            print("s150_moving_to_home")
        case _:
            print("Unknown state")


# ---------------- MAIN PROGRAM ----------------
def main() -> None:
    client = ADSClient(local_ams_net_id=LOCAL_NET_ID)
    warehouse = Warehouse()

    try:
        client.open(
            target_ip=PLC_IP,
            target_ams_net_id=PLC_NET_ID,
            target_ams_port=PLC_PORT
        )

        device_info = client.read_device_info()
        print(
            f"Connected to: {device_info.device_name} "
            f"({device_info.major_version}."
            f"{device_info.minor_version}."
            f"{device_info.build_version})"
        )

        state_prev = None

        while True:
            print("\nWaiting for system ready...")
            sleep(1)

            while True:
                state = client.read_symbol(CONVEYOR_STATE)

                if state != state_prev:
                    print_state(state)
                    state_prev = state

                if state in [101, 120, 140]:
                    break

                sleep(0.2)

            print("\n====== MENU ======")
            print("1 - Send pallet (Add stock)")
            print("2 - Release pallet from imaging")
            print("3 - Return pallet")
            print("4 - Transfer item (Remove stock)")
            print("5 - Add stock manually")
            print("6 - Remove stock manually")
            print("7 - Show stock")
            print("9 - Quit")

            try:
                sel = int(input("Select: "))
            except ValueError:
                print("Invalid input")
                continue

            match sel:

                case 1:
                    item = input("Item name: ")
                    qty = int(input("Quantity: "))
                    warehouse.add_item(item, qty)
                    client.write_symbol(REMOTE_SEND_PALLET, True)

                case 2:
                    client.write_symbol(REMOTE_RELEASE_FROM_IMAGING, True)

                case 3:
                    client.write_symbol(REMOTE_RETURN_PALLET, True)

                case 4:
                    item = input("Item name: ")
                    qty = int(input("Quantity: "))

                    if warehouse.remove_item(item, qty):
                        src_x = float(input("Source x: "))
                        src_y = float(input("Source y: "))
                        dst_x = float(input("Destination x: "))
                        dst_y = float(input("Destination y: "))

                        client.write_symbol(REMOTE_SRC_X, src_x)
                        client.write_symbol(REMOTE_SRC_Y, src_y)
                        client.write_symbol(REMOTE_DST_X, dst_x)
                        client.write_symbol(REMOTE_DST_Y, dst_y)

                        sleep(0.1)
                        client.write_symbol(REMOTE_TRANSFER_ITEM, True)

                case 5:
                    item = input("Item name: ")
                    qty = int(input("Quantity: "))
                    warehouse.add_item(item, qty)

                case 6:
                    item = input("Item name: ")
                    qty = int(input("Quantity: "))
                    warehouse.remove_item(item, qty)

                case 7:
                    warehouse.show_stock()

                case 9:
                    print("Exiting...")
                    break

                case _:
                    print("Invalid selection")

    except Exception as exc:
        print(f"Error: {exc}")

    finally:
        client.close()


if __name__ == "__main__":
    main()