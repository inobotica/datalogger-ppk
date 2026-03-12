import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable

from bleak import BleakScanner, BleakClient

SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
RX_UUID      = "12345678-1234-1234-1234-1234567890ac"  # write to ESP32
TX_UUID      = "12345678-1234-1234-1234-1234567890ad"  # notifications from ESP32
TARGET_NAME  = "MAPIR-BLE"


def default_notify_handler(data: bytes) -> None:
    print(f"[NOTIFY] {data.decode('utf-8', errors='replace')}")


@dataclass
class BLEConfig:
    target_name: str = TARGET_NAME
    rx_uuid: str = RX_UUID
    tx_uuid: str = TX_UUID
    scan_timeout_s: float = 5.0


class ThreadedBleClient:
    """
    Runs Bleak (async) inside a dedicated background thread.
    Public methods are synchronous/thread-friendly: start(), send(), stop().
    """

    def __init__(self, cfg: BLEConfig, on_notify: Callable[[bytes], None] = default_notify_handler):
        self.cfg = cfg
        self.on_notify = on_notify

        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._client: Optional[BleakClient] = None
        self._stop_evt = threading.Event()
        self._ready_evt = threading.Event()
        self._connected_evt = threading.Event()
        self._lock = threading.Lock()

    # ---------------- Thread control ----------------

    def start(self) -> None:
        print("Starting BLE Thread...")
        if self._thread and self._thread.is_alive():
            return

        self._stop_evt.clear()
        self._ready_evt.clear()
        self._connected_evt.clear()

        self._thread = threading.Thread(target=self._run_loop_thread, name="ble-thread", daemon=True)
        self._thread.start()

        # Wait until loop exists
        if not self._ready_evt.wait(timeout=10):
            raise RuntimeError("BLE thread did not initialize in time.")

    def stop(self) -> None:
        self._stop_evt.set()
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._async_disconnect(), self._loop)
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread:
            self._thread.join(timeout=5)

    def is_connected(self) -> bool:
        return self._connected_evt.is_set()

    # ---------------- Public sync API ----------------

    def send(self, text: str, response: bool = True, timeout: float = 5.0) -> None:
        """
        Thread-safe synchronous send.
        """
        if not self._loop:
            raise RuntimeError("BLE not started. Call start() first.")

        fut = asyncio.run_coroutine_threadsafe(
            self._async_write(text.encode("utf-8"), response=response),
            self._loop,
        )
        fut.result(timeout=timeout)

    def capture(self, response: bool = True, timeout: float = 5.0) -> None:
        print("Sending capture command via BLE...")
        if not self._loop:
            raise RuntimeError("BLE not started. Call start() first.")

        fut = asyncio.run_coroutine_threadsafe(
            self._async_write("on".encode("utf-8"), response=response),
            self._loop,
        )
        fut.result(timeout=timeout)


    def _run_loop_thread(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._ready_evt.set()

        # Main BLE task
        self._loop.create_task(self._async_main())

        try:
            self._loop.run_forever()
        finally:
            # Best-effort cleanup
            try:
                self._loop.run_until_complete(self._async_disconnect())
            except Exception:
                pass
            self._loop.close()

    # ---------------- Internal: async tasks ----------------

    async def _async_main(self) -> None:
        """
        Scan, connect, subscribe to notifications.
        Reconnect loop until stop requested.
        """
        while not self._stop_evt.is_set():
            try:
                address = await self._async_find_target_address()
                if not address:
                    print(f"[BLE] '{self.cfg.target_name}' not found. Retrying...")
                    await asyncio.sleep(2.0)
                    continue

                print(f"[BLE] Connecting to {self.cfg.target_name} [{address}] ...")
                async with BleakClient(address) as client:
                    self._client = client
                    if not client.is_connected:
                        print("[BLE] Connect failed. Retrying...")
                        await asyncio.sleep(2.0)
                        continue

                    self._connected_evt.set()
                    print("[BLE] Connected. Starting notify...")

                    await client.start_notify(self.cfg.tx_uuid, self._notify_cb)

                    # Stay connected until stop or disconnect
                    while not self._stop_evt.is_set() and client.is_connected:
                        await asyncio.sleep(0.25)

                    print("[BLE] Disconnecting / stopping notify...")
                    try:
                        await client.stop_notify(self.cfg.tx_uuid)
                    except Exception:
                        pass

            except Exception as e:
                print(f"[BLE] Error: {e}")
                await asyncio.sleep(2.0)
            finally:
                self._connected_evt.clear()
                self._client = None

        # Stop loop when asked
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    async def _async_find_target_address(self) -> Optional[str]:
        devices = await BleakScanner.discover(timeout=self.cfg.scan_timeout_s)
        for d in devices:
            if d.name == self.cfg.target_name:
                return d.address
        return None

    def _notify_cb(self, _sender: int, data: bytearray) -> None:
        # This callback is called from the asyncio loop thread.
        try:
            self.on_notify(bytes(data))
        except Exception as e:
            print(f"[BLE] Notify handler error: {e}")

    async def _async_write(self, payload: bytes, response: bool = True) -> None:
        if not self._client or not self._client.is_connected:
            raise RuntimeError("Not connected to BLE device.")
        await self._client.write_gatt_char(self.cfg.rx_uuid, payload, response=response)

    async def _async_disconnect(self) -> None:
        if self._client:
            try:
                if self._client.is_connected:
                    await self._client.disconnect()
            except Exception:
                pass


# ---------------- Example usage (threaded app style) ----------------

if __name__ == "__main__":
    cfg = BLEConfig()

    def on_notify(data: bytes):
        print(f"[NOTIFY] {data.decode('utf-8', errors='replace')}")

    ble = ThreadedBleClient(cfg, on_notify=on_notify)
    ble.start()

    # Wait for connection (optional)
    t0 = time.time()
    while not ble.is_connected() and time.time() - t0 < 15:
        time.sleep(0.2)

    if not ble.is_connected():
        print("Could not connect.")
        ble.stop()
        raise SystemExit(1)

    # Send some messages from the main (threaded) world
    for i in range(5):
        msg = f"hello {i}"
        print(f"[WRITE] {msg}")
        ble.send(msg)
        time.sleep(1.0)

    print("Listening for 10 seconds...")
    time.sleep(10)

    ble.stop()
    print("Done.")
