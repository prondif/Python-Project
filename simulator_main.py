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


# Try BOTH possible names (no guessing anymore)
SEND_SYMBOL = ADSSymbol("Remote.send_pallet", BOOL)
RELEASE_SYMBOL_1 = ADSSymbol("Remote.release_pallet", BOOL)
RELEASE_SYMBOL_2 = ADSSymbol("Remote.release_from_imaging", BOOL)
REMOVE_SYMBOL = ADSSymbol("Remote.return_pallet", BOOL)


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
            sleep(0.5)

            # READ SEND
            try:
                send_signal = client.read_symbol(SEND_SYMBOL)
            except Exception as e:
                print("SEND ERROR:", e)
                send_signal = False

            # READ RELEASE (try both)
            release_signal = False
            try:
                release_signal = client.read_symbol(RELEASE_SYMBOL_1)
            except Exception:
                try:
                    release_signal = client.read_symbol(RELEASE_SYMBOL_2)
                except Exception as e:
                    print("RELEASE ERROR:", e)

            # READ REMOVE
            try:
                remove_signal = client.read_symbol(REMOVE_SYMBOL)
            except Exception as e:
                print("REMOVE ERROR:", e)
                remove_signal = False

            # ALWAYS PRINT (no more silence)
            print("Signals:", send_signal, release_signal, remove_signal)

            # LOGIC
            if send_signal:
                warehouse.add_item("item", 1)
                print("Item added:", warehouse.get_stock())
                client.write_symbol(SEND_SYMBOL, False)

            if release_signal:
                print("Pallet released")
                try:
                    client.write_symbol(RELEASE_SYMBOL_1, False)
                except Exception:
                    try:
                        client.write_symbol(RELEASE_SYMBOL_2, False)
                    except Exception:
                        pass

            if remove_signal:
                success = warehouse.remove_item("item", 1)
                if success:
                    print("Item removed:", warehouse.get_stock())
                else:
                    print("Not enough stock")
                client.write_symbol(REMOVE_SYMBOL, False)

    except Exception as exc:
        print(f"Fatal Error: {exc}")

    finally:
        client.close()
        print("Connection closed")


if __name__ == "__main__":
    main()