"""Fully automatic ADS + Tier 1 Warehouse system (final version)"""

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


# ---------------- STORAGE (TOP BOX) ----------------
STORAGE_SLOTS = [
    (260.0, 120.0),
    (320.0, 120.0),
]

slot_index = 0

MAX_ITEMS = 2
processed_items = 0


# ---------------- WAREHOUSE ----------------
class Warehouse:
    def __init__(self):
        self.stock = {}

    def add_item(self, name, qty):
        self.stock[name] = self.stock.get(name, 0) + qty
        print(f"Added {qty} of {name}")

    def remove_item(self, name, qty):
        if name not in self.stock or self.stock[name] < qty:
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
def print_state(state: int) -> None:
    states = {
        101: "HOME",
        120: "IMAGING",
        140: "SLOT",
    }

    print(states.get(state, f"State {state}"))


# ---------------- AUTO TRANSFER ----------------
def auto_transfer(client, warehouse):

    global slot_index
    global processed_items

    item = warehouse.get_any_item()

    if not item:
        return False

    print(f"Transferring 1 of {item}")

    # FROM imaging
    src_x = 160.0
    src_y = 260.0

    # TO storage
    dst_x, dst_y = STORAGE_SLOTS[slot_index]

    print(f"To storage: ({dst_x}, {dst_y})")

    client.write_symbol(REMOTE_SRC_X, src_x)
    client.write_symbol(REMOTE_SRC_Y, src_y)
    client.write_symbol(REMOTE_DST_X, dst_x)
    client.write_symbol(REMOTE_DST_Y, dst_y)

    sleep(0.3)

    client.write_symbol(REMOTE_TRANSFER_ITEM, True)

    sleep(0.8)

    warehouse.remove_item(item, 1)

    processed_items += 1
    slot_index += 1

    return True


# ---------------- MAIN ----------------
def main() -> None:

    global processed_items

    client = ADSClient(local_ams_net_id=LOCAL_NET_ID)

    warehouse = Warehouse()

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

            # STOP PROGRAM AFTER 2 ITEMS
            if processed_items >= MAX_ITEMS:
                print("Processed 2 items. Program exiting.")
                break

            state = client.read_symbol(CONVEYOR_STATE)

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

                pallet_sent = True
                transfer_done = False
                released = False

                sleep(0.5)

            # ---------------- IMAGING ----------------
            elif state == 120:

                # Release pallet once
                if not released:

                    print("Releasing from imaging")

                    client.write_symbol(REMOTE_RELEASE, True)

                    released = True

                    sleep(0.5)

                # Transfer once
                elif not transfer_done:

                    success = auto_transfer(client, warehouse)

                    if success:
                        transfer_done = True

            # ---------------- SLOT ----------------
            elif state == 140 and pallet_sent:

                print("Returning pallet to home")

                client.write_symbol(REMOTE_RETURN_PALLET, True)

                pallet_sent = False
                transfer_done = True
                released = True

                sleep(1.0)
                
                # STOP after 2 transfers
                if processed_items >= MAX_ITEMS:
                    print("Finished all transfers")
                    break

            sleep(0.2)

    except KeyboardInterrupt:
        print("Stopped by user")

    finally:
        client.close()


if __name__ == "__main__":
    main()