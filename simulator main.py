"""Fully automatic ADS + Tier 1 Warehouse system"""

from __future__ import annotations

import sys
from time import sleep

try:
    from py_ads_client import ADSClient, ADSSymbol, BOOL, INT, LREAL
except ModuleNotFoundError as exc:
    if exc.name != "py_ads_client":
        raise

    print("Missing dependency: py_ads_client")
    sys.exit(1)


# ---------------- PLC CONNECTION ----------------
PLC_IP = "127.0.0.1"
PLC_NET_ID = "127.0.0.1.1.1"
PLC_PORT = 851
LOCAL_NET_ID = "127.0.0.1.1.2"

CONVEYOR_STATE = ADSSymbol("StatusVars.ConveyorState", INT)

REMOTE_SEND_PALLET = ADSSymbol("Remote.send_pallet", BOOL)
REMOTE_RELEASE = ADSSymbol("Remote.release_from_imaging", BOOL)
REMOTE_RETURN_PALLET = ADSSymbol("Remote.return_pallet", BOOL)
REMOTE_TRANSFER_ITEM = ADSSymbol("Remote.transfer_item", BOOL)

REMOTE_SRC_X = ADSSymbol("Remote.src_x", LREAL)
REMOTE_SRC_Y = ADSSymbol("Remote.src_y", LREAL)
REMOTE_DST_X = ADSSymbol("Remote.dst_x", LREAL)
REMOTE_DST_Y = ADSSymbol("Remote.dst_y", LREAL)


# ---------------- SETTINGS ----------------
MAX_ITEMS = 2
processed_items = 0


# ---------------- STORAGE SLOTS ----------------
STORAGE_SLOTS = [
    (220.0, 200.0),
    (260.0, 200.0),
]

slot_index = 0


# ---------------- WAREHOUSE ----------------
class Warehouse:

    def __init__(self):
        self.stock = {}

    def add_item(self, name, qty):
        self.stock[name] = self.stock.get(name, 0) + qty
        print(f"Added {qty} of {name}")

    def remove_item(self, name, qty):

        if name not in self.stock:
            return False

        if self.stock[name] < qty:
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


# ---------------- STATE PRINT ----------------
def print_state(state: int):

    states = {
        101: "HOME",
        120: "IMAGING",
        140: "SLOT",
    }

    print(states.get(state, f"State {state}"))


# ---------------- AUTO TRANSFER ----------------
def auto_transfer(client, warehouse):

    global processed_items
    global slot_index

    item = warehouse.get_any_item()

    if not item:
        return False

    print(f"Transferring 1 of {item}")

    # Source position (home pallet)
    src_x = 160.0
    src_y = 410.0

    # Storage position
    dst_x, dst_y = STORAGE_SLOTS[slot_index]

    print(f"Transfer position: ({dst_x}, {dst_y})")

    # Send coordinates
    client.write_symbol(REMOTE_SRC_X, src_x)
    client.write_symbol(REMOTE_SRC_Y, src_y)

    client.write_symbol(REMOTE_DST_X, dst_x)
    client.write_symbol(REMOTE_DST_Y, dst_y)

    sleep(0.5)

    # Transfer ONE box
    client.write_symbol(REMOTE_TRANSFER_ITEM, True)

    sleep(0.5)

    client.write_symbol(REMOTE_TRANSFER_ITEM, False)

    sleep(0.5)

    warehouse.remove_item(item, 1)

    processed_items += 1
    slot_index += 1

    return True


# ---------------- MAIN ----------------
def main():

    global processed_items

    client = ADSClient(local_ams_net_id=LOCAL_NET_ID)

    warehouse = Warehouse()

    # USER INPUT
    item = input("Enter item name: ")
    qty = int(input("Enter quantity: "))

    warehouse.add_item(item, qty)

    try:

        client.open(
            target_ip=PLC_IP,
            target_ams_net_id=PLC_NET_ID,
            target_ams_port=PLC_PORT
        )

        print("Connected")

        state_prev = None

        pallet_sent = False
        transfer_done = False
        released = False

        while True:

            # STOP AFTER 2 BOXES
            if processed_items >= MAX_ITEMS:
                print("All boxes stored")
                break

            state = client.read_symbol(CONVEYOR_STATE)

            # Print state only when changed
            if state != state_prev:
                print_state(state)
                state_prev = state

            # ---------------- HOME ----------------
            if (
                state == 101
                and not pallet_sent
                and processed_items < MAX_ITEMS
            ):

                print("Sending pallet")

                client.write_symbol(REMOTE_SEND_PALLET, True)

                sleep(0.5)

                client.write_symbol(REMOTE_SEND_PALLET, False)

                pallet_sent = True
                transfer_done = False
                released = False

                sleep(0.5)

            # ---------------- IMAGING ----------------
            elif state == 120:

                print("Releasing from imaging")

                client.write_symbol(REMOTE_RELEASE, True)

                sleep(0.5)

                client.write_symbol(REMOTE_RELEASE, False)

                sleep(0.5)

                success = auto_transfer(client, warehouse)

                if success:
                    transfer_done = True

                sleep(1.0)

            # ---------------- SLOT ----------------
            elif state == 140 and pallet_sent:

                print("Returning pallet to home")

                print("Sending return command")

                client.write_symbol(REMOTE_RETURN_PALLET, True)

                sleep(2.0)

                client.write_symbol(REMOTE_RETURN_PALLET, False)

                print("Return command finished")

                pallet_sent = False
                transfer_done = False
                released = False

                sleep(2.0)

                if processed_items >= MAX_ITEMS:
                    print("All boxes stored")

                    sleep(8)

                    break

            sleep(0.2)

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        client.close()


if __name__ == "__main__":
    main()