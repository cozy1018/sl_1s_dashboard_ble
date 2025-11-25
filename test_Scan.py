import asyncio
from bleak import BleakScanner


async def scan():
    print("🔍 Scanning for ALL devices for 10 seconds...")
    print("Make sure NO other app is connected to the board!\n")

    devices = await BleakScanner.discover(timeout=10.0)

    print(f"\n✅ Scan complete! Found {len(devices)} devices:\n")

    for d in devices:
        print(f"📱 Name: {d.name or 'Unknown'}")
        print(f"   Address: {d.address}")
        print("   ---")


asyncio.run(scan())