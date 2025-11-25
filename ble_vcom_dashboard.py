"""
Bluetooth version of vcom_with_dashboard.py
Replaces USB Serial with Bluetooth BLE
"""

import asyncio
from bleak import BleakClient, BleakScanner
import threading
import time
from ecg_dashboard import ECGDashboard, ECGDashboardIntegration

# Bluetooth configuration
DEVICE_NAME = "ecg_sensor_bt"
SPP_TX_CHAR_UUID = "fec26ec4-6d71-4442-9f81-55bc21d658d6"

# Global variable for dashboard integration
dashboard_integration = None
running = True


def notification_handler(sender, data):
    """
    Bluetooth callback function
    Replaces USB serial.read() in vcom_with_dashboard.py
    """
    global dashboard_integration
    try:
        text = data.decode('utf-8').strip()
        if text:
            # Convert to ECG value
            ecg_value = int(text) / 255.0

            # Send to dashboard (same as USB version)
            dashboard_integration.process_new_sample(ecg_value)

    except Exception as e:
        print(f"Error processing data: {e}")


async def ble_connect():
    """
    Connect to Bluetooth device and receive data
    Replaces USB serial connection in vcom_with_dashboard.py
    """
    global running

    print("🔍 Scanning for ecg_sensor_bt...")

    # Scan for devices
    devices = await BleakScanner.discover(timeout=10.0)

    # Find target device
    target = None
    for d in devices:
        if d.name == DEVICE_NAME:
            target = d
            print(f"✅ Found: {d.name} at {d.address}")
            break

    if not target:
        print("❌ Device not found!")
        print("Make sure:")
        print("  - Board is powered on")
        print("  - Bluetooth is enabled")
        print("  - No other app is connected to the board")
        return

    print(f"🔗 Connecting to {target.name}...")

    try:
        # Connect to device
        async with BleakClient(target) as client:
            print("✅ Connected!")

            # Start receiving notifications
            await client.start_notify(SPP_TX_CHAR_UUID, notification_handler)
            print("✅ Receiving ECG data via Bluetooth...\n")

            # Keep connection alive
            while running:
                await asyncio.sleep(0.1)

    except Exception as e:
        print(f"❌ Bluetooth error: {e}")

    finally:
        print("\n📡 Bluetooth disconnected")


def main():
    """
    Main function - Bluetooth version
    """
    global dashboard_integration, running

    print("=" * 70)
    print("  BLE ECG Dashboard")
    print("  Bluetooth version of vcom_with_dashboard.py")
    print("=" * 70)
    print()

    # Create dashboard (same as USB version)
    print("Initializing ECG Dashboard...")
    dashboard = ECGDashboard(window_size=1250, sampling_rate=125)
    dashboard_integration = ECGDashboardIntegration(dashboard)
    print("✅ Dashboard initialized\n")

    # Start Bluetooth in background thread
    def run_ble():
        asyncio.run(ble_connect())

    print("Starting Bluetooth connection in background...")
    ble_thread = threading.Thread(target=run_ble, daemon=True, name="BLE-Thread")
    ble_thread.start()

    # Wait for connection to establish
    print("Waiting for Bluetooth connection...")
    time.sleep(3)

    # Start dashboard in main thread (same as USB version)
    print("Starting dashboard GUI...\n")
    try:
        dashboard.start_dashboard(interval=20)
    except KeyboardInterrupt:
        print("\n👋 Received Ctrl+C, stopping...")
    finally:
        running = False
        if ble_thread.is_alive():
            print("Waiting for Bluetooth thread to finish...")
            ble_thread.join(timeout=2.0)

    print("\n✅ Program finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()