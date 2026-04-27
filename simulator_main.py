from __future__ import annotations

import sys
from time import sleep
from warehouse import Warehouse

try:
    from py_ads_client import ADSClient, ADSSymbol, BOOL
except ModuleNotFoundError:
    print("Missing dependency: py_ads_client")
    sys.exit(1)


PLC_IP = "127.0.0.1"
PLC_NET_ID = "127.0.0.1.1.1"
PLC_PORT = 851
LOCAL_NET_ID = "127.0.0.1.1.2"

# Use same symbols as reference
REMOTE_SEND = ADSSymbol("Remote.send_pallet", BOOL)
REMOTE_REMOVE = ADSSymbol("Remote.return_pallet", BOOL)


def main():
    warehouse = Warehouse()
    client = ADSClient(local_ams_net_id=LOCAL_NET_ID)

    try:
        client.open(target_ip=PLC_IP, target_ams_net_id=PLC_NET_ID, target_ams_port=PLC_PORT)
        print("Connected to simulator")

        while True:
            sleep(0.5)

            # Add item when simulator sends signal
            if client.read_symbol(REMOTE_SEND):
                warehouse.add_item("item", 1)
                print("Item added:", warehouse.get_stock())
                client.write_symbol(REMOTE_SEND, False)

            # Remove item when simulator sends signal
            if client.read_symbol(REMOTE_REMOVE):
                success = warehouse.remove_item("item", 1)
                print("Removed" if success else "Not enough stock")
                client.write_symbol(REMOTE_REMOVE, False)

    except Exception as exc:
        print(f"Error: {exc}")

    finally:
        client.close()


if __name__ == "__main__":
    main()