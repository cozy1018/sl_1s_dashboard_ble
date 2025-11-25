# sl_1s_dashboard_ble

Python-based tools and dashboards for debugging the single-lead ventricular dysfunction detection project.

## Overview
This repository includes multiple scripts to visualize ECG data, test BLE connectivity, and interact with the Silicon Labs board.

## USB VCOM Dashboard
Connect the Silicon Labs board to a USB port, then execute:

```bash
python vcom_with_dashboard.py
```

Stop execution with **Ctrl + C** or by closing the plot window.  
If running again, **reset the Silicon Labs board** to clear the buffers.

### Changing the ECG Data Source
Modify line 490:

```python
array_to_send = ecg_long_data_normal
```

Available options:

- `ecg_long_data_normal` / `ecg_long_data_PVC` (external CSV files)
- `ecg_data_normal` / `ecg_data_PVC` (hardcoded in `vcom_with_dashboard.py`)

---

## !! New Files Added !!

### **BLE VCOM Dashboard**

```bash
python ble_vcom_dashboard.py
```

A Bluetooth version of the dashboard.  
Used to receive ECG-like data streams via BLE instead of USB.

### **BLE Scan Test**

```bash
python test_Scan.py
```

Simple BLE scanning script to detect nearby BLE devices and verify connectivity.

---

## Files Included
- `vcom_with_dashboard.py` – main VCOM dashboard  
- `ble_vcom_dashboard.py` – BLE dashboard (new)  
- `test_Scan.py` – BLE device scanner (new)  
- `ecg_dashboard.py` – ECG visualization  
