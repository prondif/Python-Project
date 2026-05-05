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

    def has_stock(self):
        return len(self.stock) > 0


# ---------------- STATE PRINT ----------------
def print_state(state: int) -> None:
    states = {
        0: "s000_initialize",
        1: "s001_not_homed",
        10: "s010_homing",
        100: "s100_braking",
        101: "s101_waiting_at_home",
        110: "s110_moving_to_imaging",
        120: "s120_imaging",
        130: "s130_moving_to_slot",
        140: "s140_waiting_in_slot",
        150: "s150_moving_to_home",
    }
    print(states.get(state, "Unknown state"))


# ---------------- AUTO TRANSFER ----------------
def auto_transfer(client, warehouse):
    item = warehouse.get_any_item()

    if not item:
        print("No stock available")
        return False

    print(f"Auto transferring 1 of {item}")

    # Imaging position
    src_x = 160.0
    src_y = 260.0

    # Transfer position
    dst_x = 160.0
    dst_y = 200.0

    client.write_symbol(REMOTE_SRC_X, src_x)
    client.write_symbol(REMOTE_SRC_Y, src_y)
    client.write_symbol(REMOTE_DST_X, dst_x)
    client.write_symbol(REMOTE_DST_Y, dst_y)

    sleep(0.2)

    # Transfer item
    client.write_symbol(REMOTE_TRANSFER_ITEM, True)

    sleep(0.4)

    warehouse.remove_item(item, 1)

    return True


# ---------------- MAIN ----------------
def main() -> None:
    client = ADSClient(local_ams_net_id=LOCAL_NET_ID)
    warehouse = Warehouse()

    # Initial input
    item = input("Enter item name: ")
    qty = int(input("Enter quantity: "))
    warehouse.add_item(item, qty)

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
        pallet_sent = False
        transfer_done = False
        released = False

        # MAIN LOOP
        while True:
            state = client.read_symbol(CONVEYOR_STATE)

            if state != state_prev:
                print_state(state)
                state_prev = state

            # ---------------- HOME ----------------
            if state == 101 and not pallet_sent:
                if warehouse.has_stock():
                    print("Sending pallet to imaging")
                    client.write_symbol(REMOTE_SEND_PALLET, True)
                    pallet_sent = True

                transfer_done = False
                released = False

            # ---------------- IMAGING ----------------
            elif state == 120:

                # STEP 1: release pallet
                if not released:
                    print("Releasing pallet from imaging")
                    client.write_symbol(REMOTE_RELEASE, True)
                    sleep(0.3)
                    released = True

                # STEP 2: transfer item
                elif not transfer_done:
                    success = auto_transfer(client, warehouse)
                    if success:
                        transfer_done = True

            # ---------------- SLOT ----------------
            elif state == 140 and pallet_sent:
                print("Returning pallet to home")
                client.write_symbol(REMOTE_RETURN_PALLET, True)
                pallet_sent = False

            sleep(0.2)

    except Exception as exc:
        print(f"Error: {exc}")

    finally:
        client.close()


if __name__ == "__main__":
    main()