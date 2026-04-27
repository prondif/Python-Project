from __future__ import annotations

import sys
from time import sleep
from warehouse import Warehouse

try:
    from py_ads_client import ADSClient, ADSSymbol, BOOL
except ModuleNotFoundError:
    print("Missing dependency: py_ads_client")
    sys.exit(1)


# Connection settings
PLC_IP = "127.0.0.1"
PLC_NET_ID = "127.0.0.1.1.1"
PLC_PORT = 851
LOCAL_NET_ID = "127.0.0.1.1.2"


# ADS symbols
REMOTE_SEND = ADSSymbol("Remote.send_pallet", BOOL)
REMOTE_RELEASE = ADSSymbol("Remote.release_from_imaging", BOOL)
REMOTE_REMOVE = ADSSymbol("Remote.return_pallet", BOOL)


def main():
    warehouse = Warehouse()
    client = ADSClient(local_ams_net_id=LOCAL_NET_ID)

    try:
        client.open(
            target_ip=PLC_IP,
            target_ams_net_id=PLC_NET_ID,
            target_ams_port=PLC_PORT
        )

        device_info = client.read_device_info()
        print(f"Connected to: {device_info.device_name}")
        print("Waiting for signals...")

        while True:
            sleep(0.2)

            try:
                send_signal = client.read_symbol(REMOTE_SEND)
                release_signal = client.read_symbol(REMOTE_RELEASE)
                remove_signal = client.read_symbol(REMOTE_REMOVE)
            except Exception:
                continue
           
            print(send_signal, release_signal, remove_signal)

            if send_signal:
                warehouse.add_item("item", 1)
                print("Item added:", warehouse.get_stock())
                client.write_symbol(REMOTE_SEND, False)

            if release_signal:
                print("Pallet released from imaging")
                client.write_symbol(REMOTE_RELEASE, False)

            if remove_signal:
                success = warehouse.remove_item("item", 1)
                if success:
                    print("Item removed:", warehouse.get_stock())
                else:
                    print("Not enough stock")
                client.write_symbol(REMOTE_REMOVE, False)

    except Exception as exc:
        print(f"Error: {exc}")

    finally:
        client.close()
        print("Connection closed")


if __name__ == "__main__":
    main()