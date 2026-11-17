import asyncio
from bleak import BleakScanner

# Explicitly verified lowercase MAC target
TARGET_MAC = "c0:2c:ed:49:01:4b"

# Track the last known state to prevent repetitive spam
current_state = None


def decode_shelly_packet(device, advertising_data):
    global current_state

    if device.address.lower() != TARGET_MAC:
        return

    service_data = advertising_data.service_data
    if not service_data:
        return

    for uuid, data in service_data.items():
        payload = list(data)

        # Scan through the BTHome byte string for the true window/door tag (0x2D)
        for i in range(len(payload) - 1):
            data_type = payload[i]

            if (
                data_type == 0x2D
            ):  # 0x2D is the official BTHome window/door sensor object ID
                raw_value = payload[i + 1]

                # BTHome V2 Spec: 1 = OPENED, 0 = CLOSED
                new_state = "⚠️ OPENED" if raw_value == 1 else "🔒 CLOSED"

                # Only log when a real physical transition happens
                if new_state != current_state:
                    current_state = new_state
                    print(
                        f"Sensor State: {current_state} (Signal: {advertising_data.rssi} dBm)"
                    )
                return


async def main():
    print(f"🚀 Windows Engine Active. Monitoring Shelly ({TARGET_MAC})...")
    scanner = BleakScanner(detection_callback=decode_shelly_packet)
    await scanner.start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
