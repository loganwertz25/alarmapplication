import asyncio
from bleak import BleakScanner

TARGET_MAC = "c0:2c:ed:49:01:4b"


class ShellyEngine:
    def __init__(self, state_changed_callback):
        self.scanner = None
        self.current_state = None
        self.state_changed_callback = state_changed_callback
        self.loop = asyncio.get_running_loop()

    def decode_shelly_packet(self, device, advertising_data):
        if device.address.lower() != TARGET_MAC.lower():
            return

        service_data = advertising_data.service_data
        if not service_data:
            return

        for uuid, data in service_data.items():
            payload = list(data)
            # battery = payload[4]
            for i in range(len(payload) - 1):
                data_type = payload[i]

                if data_type == 0x2D:
                    raw_value = payload[i + 1]
                    new_state = "OPENED" if raw_value == 1 else "CLOSED"

                    if new_state != self.current_state:
                        self.current_state = new_state
                        # Safely route back to the main Tkinter thread loop
                        self.loop.call_soon_threadsafe(
                            self.state_changed_callback,
                            new_state,
                            advertising_data.rssi,
                        )
                    return

    async def start(self):
        self.scanner = BleakScanner(detection_callback=self.decode_shelly_packet)

        # 🔑 FIX: Offload the winrt initialization to an executor thread to establish MTA compliance
        await self.loop.run_in_executor(None, self._sync_start)

    def _sync_start(self):
        """Synchronous wrapper executed on the background worker thread pool"""
        # We run the async start loop within the thread-safe future context
        future = asyncio.run_coroutine_threadsafe(self.scanner.start(), self.loop)
        future.result()  # Blocks background thread until initialized safely

    async def stop(self):
        if self.scanner:
            # Offload stopping to the executor thread too just to be clean
            await self.loop.run_in_executor(None, self._sync_stop)

    def _sync_stop(self):
        future = asyncio.run_coroutine_threadsafe(self.scanner.stop(), self.loop)
        future.result()
