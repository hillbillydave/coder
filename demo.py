# demo.py
from workers.shop_code_worker import ShopCodeWorker
from connector import FakeElm327Connector
import threading

worker = ShopCodeWorker({"use_db": False})
print("M18 Battery Integration for Chevy Volt:")
worker.execute_task(["battery_integration", "1"], threading.Event())

print("\nOBD-II Scan:")
worker.execute_task(["obdii_scan", "1", "basic"], threading.Event())

print("\nWiFi Diagnostics:")
worker.execute_task(["wifi_diagnostics", "1"], threading.Event())
