import serial
import time
import threading
from queue import Queue

ecg_data_PVC = [
0.2981,0.2896,0.2949,0.2842,0.2832,0.2769,0.2921,0.2866,0.2810,0.2717,0.2791,0.2788,0.2911,0.2720,0.2772,0.2770,0.2815,0.2855,0.2738,0.2903,
0.2844,0.2707,0.2844,0.2874,0.2907,0.3050,0.3156,0.3332,0.3637,0.3670,0.3702,0.3756,0.3341,0.3231,0.2876,0.2881,0.2862,0.2840,0.2823,0.2681,
0.2608,0.4882,0.8598,0.9648,0.7666,0.2540,0.1997,0.2491,0.2567,0.2694,0.2710,0.2606,0.2656,0.2479,0.2654,0.2696,0.2716,0.2559,0.2755,0.2731,
0.2926,0.2881,0.2883,0.2968,0.3026,0.3051,0.3257,0.3266,0.3367,0.3669,0.3697,0.3911,0.4282,0.4518,0.4703,0.5121,0.5226,0.5336,0.5339,0.5291,
0.5076,0.4933,0.4610,0.4478,0.4192,0.3904,0.3774,0.3663,0.3524,0.3361,0.3262,0.3278,0.3100,0.2959,0.3073,0.2927,0.2941,0.2979,0.3039,0.2999,
0.3141,0.3034,0.3102,0.3152,0.3284,0.3321,0.3474,0.3676,0.4195,0.4553,0.5430,0.6690,0.7463,0.6566,0.4985,0.1691,0.0081,0.0555,0.0515,0.0356,
0.0528,0.1071,0.1661,0.2090,0.2383,0.2831,0.2928,0.3096,0.3089,0.3144,0.3339,0.3368,0.3185,0.3463,0.3248,0.3359,0.3457,0.3715,0.3826,0.4128,
0.4389,0.4682,0.4925,0.5343,0.5753,0.6174,0.6151,0.6303,0.6386,0.6116,0.5951,0.5590,0.5352,0.4972,0.4637,0.4324,0.4232,0.3957,0.3783,0.3553,
0.3585,0.3496,0.3547,0.3450,0.3530,0.3599,0.3967,0.4332,0.4846,0.5651,0.6654,0.7504,0.8254,0.8350,0.7866,0.7796,0.7316,0.4685,0.2901,0.2595,
0.2298,0.2010,0.1639,0.1652,0.1590,0.1559,0.1628,0.1768,0.1664,0.1588,0.1518,0.1450,0.1360,0.1192,0.1111,0.0973,0.0877,0.0840,0.0854,0.0866,
0.0953,0.1093,0.1473,0.1572,0.1871,0.2095,0.2441,0.2625,0.3051,0.2862,0.2805,0.3012,0.3084,0.3077,0.3247,0.3210,0.3051,0.3101,0.3104,0.3281,
0.3194,0.3006,0.3053,0.3065,0.3156,0.3168,0.3123,0.3194,0.3122,0.3299,0.3227,0.3173,0.3103,0.3232,0.3234,0.3221,0.3050,0.3218,0.3194,0.3215,
0.3144,0.3181,0.3092,0.3176,0.3163,0.3247,0.3268,0.3287,0.3255,0.3151,0.3317,0.3177,0.3268,0.3257,0.3274,0.3232,0.3327,0.3318,0.3399,0.3217,
0.3394,0.3156,0.3280,0.3285,0.3396,0.3298,0.3351,0.3281,0.3351,0.3272,0.3340,0.3376,0.3362,0.3384,0.3376,0.3439,0.3325,0.3378,0.3377,0.3419,
0.3315,0.3377,0.3377,0.3527,0.3385,0.3425,0.3375,0.3423,0.3389,0.3404,0.3391,0.3508,0.3435,0.3416,0.3412,0.3415,0.3478,0.3446,0.3465,0.3489,
0.3523,0.3238,0.3537,0.3455,0.3587,0.3494,0.3517,0.3578,0.3938,0.3798,0.4299,0.4370,0.4417,0.4239,0.3959,0.3737,0.3678,0.3495,0.3592,0.3510,
0.3341,0.3180,0.5908,0.9219,1.0000,0.6979,0.2617,0.3111,0.3217,0.3368,0.3236,0.3267,0.3126,0.3336,0.3300,0.3310,0.3116,0.3275,0.3288,0.3353,
0.3292,0.3368,0.3520,0.3582,0.3492,0.3711,0.3946,0.3807,0.4011,0.4332,0.4494,0.4784,0.5083,0.5311,0.5562,0.5681,0.5865,0.5821,0.5880,0.5504,
0.5427,0.5156,0.5015,0.4744,0.4603,0.4367,0.4234,0.4172,0.4012,0.3972,0.3790,0.3756,0.3696,0.3736,0.3703,0.3772,0.3735,0.3820,0.3736,0.3895,
0.3983,0.4457,0.4618,0.5137,0.6406,0.7279,0.6462,0.3999,0.0186,0.0005,0.0768,0.0676,0.0746,0.1091,0.1467,0.2007,0.2588,0.2867,0.3054,0.3087,
0.3500,0.3337,0.3370,0.3423,0.3612,0.3513,0.3682,0.3636,0.3836,0.3832,0.4032,0.4225,0.4544,0.4813,0.5267,0.5545,0.5870,0.6121,0.6226,0.6292,
0.6250,0.6221,0.5978,0.5765,0.5463,0.5238,0.4939,0.4751,0.4523,0.4336,0.4048,0.4094,0.4000,0.3965,0.3804,0.4021,0.4054,0.4463,0.4932,0.5661,
0.6300,0.7224,0.7969,0.8134,0.7937,0.6987,0.6559,0.6375,0.5017,0.3508,0.2909,0.2519,0.2416,0.2177,0.1947,0.1713,0.1757,0.1675,0.1678,0.1716,
0.1720,0.1710,0.1840,0.1683,0.1652,0.1511,0.1455,0.1308,0.1357,0.1274,0.1397,0.1287,0.1249,0.1526,0.1601,0.1937,0.2077,0.2463,0.2623,0.2925,
0.3026,0.3252,0.3324,0.3432,0.3444,0.3560,0.3439,0.3558,0.3389,0.3424,0.3399,0.3411,0.3393,0.3412,0.3344,0.3322,0.3356,0.3350,0.3391,0.3381,
0.3332,0.3281,0.3393,0.3307,0.3411,0.3292,0.3323,0.3280,0.3271,0.3236,0.3310,0.3242,0.3241,0.3235,0.3272,0.3261,0.3293,0.3155,0.3210,0.3211,
0.3101,0.3125,0.3260,0.3147,0.3142,0.3221,0.3147,0.3172,0.3205,0.3248,0.3223,0.3345,0.3143,0.3229,0.3159,0.3265,0.3161,0.3257,0.3284,0.3302,
0.3218,0.3280,0.3275,0.3301,0.3291,0.3270,0.3287,0.3212,0.3307,0.3285,0.3311,0.3301,0.3390,0.3346,0.3353,0.3286,0.3383,0.3318,0.3407,0.3344,
0.3431,0.3354,0.3349,0.3317,0.3427,0.3411,0.3492,0.3493,0.3390,0.3383,0.3420,0.3441,0.3434,0.3425,0.3398,0.3416,0.3454,0.3470,0.3421,0.3596,
0.3461,0.3511,0.3431,0.3531,0.3460,0.3469,0.3504,0.3544,0.3531,0.3599,0.3553,0.3648,0.3655,0.3653,0.3839,0.3909,0.4181,0.4488,0.4533,0.4560,
0.4489,0.3933,0.3833,0.3633,0.3705,0.3520,0.3663,0.3450,0.3303,0.3639,0.7009,0.9466,0.9782,0.6082,0.2414,0.3173,0.3150,0.3359,0.3285,0.3332,
0.3199,0.3292,0.3247,0.3357,0.3262
]

ecg_data_normal = [
0.1467,0.1461,0.1352,0.1073,0.0402,0.0164,0.1867,0.5909,0.8462,0.3880,0.0474,0.1252,0.1003,0.1209,0.0933,0.1173,0.0960,0.1075,0.1002,0.1149,
0.1027,0.1100,0.1041,0.1088,0.1056,0.1064,0.1034,0.1024,0.1079,0.1048,0.1048,0.1131,0.1134,0.1040,0.1145,0.0986,0.1084,0.0866,0.1017,0.0878,
0.1011,0.0879,0.0916,0.0894,0.1007,0.1059,0.1224,0.1351,0.1380,0.1459,0.1523,0.1546,0.1574,0.1531,0.1440,0.1507,0.1380,0.1384,0.1289,0.1491,
0.1351,0.1374,0.1258,0.1408,0.1237,0.1293,0.1197,0.1242,0.1254,0.1288,0.1199,0.1294,0.1207,0.1253,0.1286,0.1277,0.1190,0.1118,0.1188,0.1277,
0.1368,0.1317,0.1443,0.1490,0.1654,0.1645,0.1866,0.1773,0.1774,0.1740,0.1726,0.1762,0.1739,0.1218,0.1239,0.0962,0.1093,0.1028,0.1037,0.0991,
0.1034,0.1016,0.0937,0.0598,0.0011,0.0004,0.2025,0.6086,0.8409,0.3613,0.0151,0.0712,0.0644,0.0854,0.0705,0.0844,0.0752,0.0911,0.0758,0.0917,
0.0875,0.0882,0.0688,0.0724,0.0753,0.0810,0.0839,0.0827,0.0779,0.0763,0.0747,0.0703,0.0775,0.0713,0.0801,0.0699,0.0802,0.0654,0.0693,0.0479,
0.0525,0.0406,0.0470,0.0498,0.0746,0.0793,0.0996,0.1104,0.1271,0.1350,0.1428,0.1444,0.1508,0.1560,0.1486,0.1486,0.1413,0.1437,0.1261,0.1407,
0.1356,0.1488,0.1342,0.1422,0.1249,0.1355,0.1278,0.1297,0.1226,0.1295,0.1190,0.1244,0.1207,0.1283,0.1241,0.1268,0.1332,0.1296,0.1326,0.1254,
0.1246,0.1249,0.1353,0.1335,0.1645,0.1733,0.1819,0.1824,0.2059,0.1933,0.1935,0.1779,0.1913,0.1808,0.2088,0.1691,0.1563,0.1252,0.1226,0.1237,
0.1218,0.1214,0.1249,0.1226,0.1272,0.1224,0.1205,0.0753,0.0346,0.0000,0.1341,0.4813,0.8792,0.6848,0.0873,0.0966,0.1050,0.1135,0.0958,0.1113,
0.1011,0.1140,0.1036,0.1106,0.1068,0.1139,0.1078,0.1060,0.1062,0.1036,0.1096,0.0996,0.1128,0.1059,0.1197,0.1134,0.1163,0.1054,0.1131,0.1034,
0.1081,0.1008,0.1091,0.0982,0.0993,0.0992,0.1065,0.1038,0.1089,0.1174,0.1344,0.1481,0.1603,0.1707,0.1712,0.1876,0.1825,0.1855,0.1736,0.1858,
0.1741,0.1843,0.1715,0.1883,0.1749,0.1893,0.1715,0.1759,0.1652,0.1746,0.1648,0.1696,0.1663,0.1669,0.1600,0.1569,0.1587,0.1531,0.1572,0.1577,
0.1647,0.1580,0.1738,0.1652,0.1700,0.1615,0.1668,0.1600,0.1918,0.1972,0.2150,0.1948,0.2146,0.2175,0.2288,0.2208,0.2180,0.2147,0.2159,0.2340,
0.2013,0.1750,0.1576,0.1547,0.1412,0.1511,0.1397,0.1452,0.1380,0.1531,0.1270,0.0880,0.0226,0.0344,0.2216,0.5960,0.9059,0.5328,0.0731,0.1176,
0.1199,0.1373,0.1225,0.1281,0.1274,0.1289,0.1230,0.1241,0.1269,0.1244,0.1284,0.1283,0.1312,0.1278,0.1375,0.1245,0.1274,0.1183,0.1324,0.1208,
0.1393,0.1324,0.1376,0.1255,0.1318,0.1231,0.1239,0.1177,0.1200,0.1196,0.1227,0.1261,0.1288,0.1396,0.1404,0.1594,0.1650,0.1807,0.1752,0.1927,
0.1838,0.1965,0.1811,0.1927,0.1856,0.1905,0.1731,0.1820,0.1722,0.1790,0.1657,0.1745,0.1692,0.1734,0.1734,0.1629,0.1629,0.1609,0.1627,0.1576,
0.1671,0.1612,0.1667,0.1562,0.1673,0.1520,0.1610,0.1554,0.1691,0.1633,0.1711,0.1713,0.2052,0.1912,0.2157,0.2275,0.2341,0.2289,0.2222,0.2166,
0.2046,0.2269,0.2441,0.2186,0.1793,0.1727,0.1512,0.1626,0.1472,0.1456,0.1344,0.1464,0.1379,0.1432,0.0984,0.0670,0.0113,0.1717,0.4938,0.8574,
0.5869,0.1080,0.0755,0.1110,0.1103,0.1244,0.1291,0.1164,0.1220,0.1111,0.1218,0.1142,0.1209,0.1094,0.1200,0.1130,0.1274,0.1152,0.1151,0.1039,
0.1171,0.1088,0.1193,0.1151,0.1244,0.1176,0.1268,0.1283,0.1272,0.1228,0.1138,0.1125,0.0970,0.0994,0.1046,0.1044,0.1042,0.1163,0.1186,0.1451,
0.1496,0.1679,0.1647,0.1794,0.1729,0.1804,0.1695,0.1794,0.1665,0.1682,0.1616,0.1666,0.1654,0.1630,0.1648,0.1607,0.1584,0.1536,0.1573,0.1446,
0.1530,0.1452,0.1551,0.1495,0.1470,0.1416,0.1664,0.1551,0.1521,0.1417,0.1525,0.1486,0.1588,0.1505,0.1606,0.1809,0.2005,0.1943,0.2144,0.2175,
0.2153,0.2081,0.1949,0.1960,0.2007,0.1778,0.1475,0.1532,0.1452,0.1437,0.1280,0.1388,0.1277,0.1375,0.1343,0.1333,0.0894,0.0343,0.0501,0.3117,
0.7056,0.8444,0.2972,0.0549,0.1116,0.1196,0.1276,0.1140,0.1190,0.1129,0.1214,0.1090,0.1114,0.1075,0.1091,0.1037,0.1156,0.1104,0.1136,0.1058,
0.1104,0.0999,0.1149,0.1055,0.1093,0.1084,0.1197,0.1078,0.1069,0.0960,0.0853,0.0808,0.0782,0.0867,0.0823,0.0864,0.0824,0.1021,0.1164,0.1395,
0.1527,0.1702,0.1660,0.1825,0.1680,0.1806,0.1729,0.1774,0.1655,0.1790,0.1648,0.1668,0.1630,0.1639,0.1639,0.1639,0.1638,0.1533,0.1549,0.1497,
0.1587,0.1537,0.1601,0.1499,0.1524,0.1458,0.1579,0.1456,0.1547,0.1491,0.1621,0.1508,0.1617,0.1487,0.1747,0.1974,0.2040,0.2203,0.2248,0.2174,
0.2117,0.2116,0.1970,0.2237,0.2046,0.1737,0.1538,0.1482,0.1371,0.1449,0.1342,0.1495,0.1400,0.1459,0.0874,0.0350,0.0410,0.3084,0.7233,1.0000,
0.6613,0.2729,0.0816,0.0303,0.1123
]

#load csv files into lists
import csv
def load_csv_to_list(filename):
    data_list = []
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            for item in row:
                try:
                    data_list.append(float(item))
                except ValueError:
                    pass  # Ignore non-numeric values
    return data_list

ecg_long_data_normal = load_csv_to_list('Normal.csv')
ecg_long_data_PVC = load_csv_to_list('PVC.csv')


#########################  CHANGE THE ARRAY NAME HERE #############################
array_to_send = ecg_long_data_PVC  # Change this to send different data   (options are: ecg_data_PVC, ecg_data_normal, ecg_long_data_normal, ecg_long_data_PVC)
###################################################################################
# Helper function to connect to the serial port
def connect_to_serial(port, baudrate):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=0,           # Non-blocking read operations
            write_timeout=1,     # Timeout for write operations
            rtscts=False,        # Disable hardware flow control
            xonxoff=False        # Disable software flow control
        )
        print(f"Successfully connected to {port}.")
        return ser
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {port}.")
        return None

# Helper function to send a message over the serial connection (TX only)
def send_message(ser, message, send_count):
    if not ser or not ser.is_open:
        print("Serial port is not open.")
        return

    try:
        message_bytes = (message + '\0').encode('utf-8')
        ser.write(message_bytes)
        
        # Optional debug print (uncomment if needed)
        # if send_count % 10 == 0:
        #     print(f"Sent: '{message}' (count: {send_count})")

    except serial.SerialTimeoutException:
        print("Write timeout.")
    except Exception as e:
        print(f"An error occurred while sending: {e}")

# Thread function for receiving data (RX only)
def receive_thread(ser, response_queue, stop_event):
    """Continuously read from serial port and put responses in queue"""
    buffer = ""
    print("RX Thread: Started")
    
    while not stop_event.is_set():
        if ser and ser.is_open:
            try:
                # Only read if data is available - completely non-blocking
                bytes_available = ser.in_waiting
                if bytes_available > 0:
                    # Read all available bytes without blocking
                    data = ser.read(bytes_available).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Process complete lines from buffer
                    while '\n' in buffer or '\r' in buffer:
                        if '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                        else:
                            line, buffer = buffer.split('\r', 1)
                        
                        line = line.strip()
                        if line:
                            response_queue.put(line)
                            
            except Exception as e:
                print(f"Error reading from serial: {e}")
                break
        time.sleep(0.001)  # Small delay to prevent busy waiting
    
    print("RX Thread: Stopping")

# Thread function for transmitting data at precise intervals
def transmit_thread(ser, data_list, interval_seconds, stop_event):
    """Transmit data at precise intervals"""
    data_index = 0
    send_count = 0
    
    while not stop_event.is_set() and data_index < len(data_list):
        start_time = time.time()
        
        # Send the data
        string_to_send = str(data_list[data_index])
        send_message(ser, string_to_send, send_count)
        
        data_index += 1
        send_count += 1
        
        # Calculate sleep time to maintain precise interval
        elapsed = time.time() - start_time
        sleep_time = max(0, interval_seconds - elapsed)
        time.sleep(sleep_time)
    
    print(f"TX Thread: Finished sending {send_count} data points.")

# Utility function to check thread status
def check_thread_status(*threads):
    """Check and report the status of multiple threads"""
    print("\n--- Thread Status Check ---")
    all_finished = True
    
    for i, thread in enumerate(threads):
        if thread is not None:
            status = "RUNNING" if thread.is_alive() else "FINISHED"
            thread_name = getattr(thread, 'name', f'Thread-{i+1}')
            print(f"{thread_name}: {status}")
            if thread.is_alive():
                all_finished = False
        else:
            print(f"Thread-{i+1}: NOT CREATED")
    
    print(f"All threads finished: {all_finished}")
    return all_finished


if __name__ == "__main__":
    # CONFIGURATION
    port_name = "COM3"
    baud_rate = 115200
    interval_seconds = 0.008    # 125Hz
    
    ser_connection = None  # Initialize connection variable
    
    # Threading synchronization
    stop_event = threading.Event()
    response_queue = Queue()

    try:
        # Open serial connection
        ser_connection = connect_to_serial(port_name, baud_rate)

        if ser_connection:
            print(f"Starting decoupled TX/RX communication every {interval_seconds * 1000}ms. Ctrl+C to stop.")
            
            # Start the receive thread
            rx_thread = threading.Thread(
                target=receive_thread, 
                args=(ser_connection, response_queue, stop_event),
                name="RX-Thread",
                daemon=True
            )
            rx_thread.start()
            
            # Start the transmit thread
            tx_thread = threading.Thread(
                target=transmit_thread,
                args=(ser_connection, array_to_send, interval_seconds, stop_event),
                name="TX-Thread",
                daemon=True
            )
            tx_thread.start()
            
            # Main thread handles received messages and monitors progress
            messages_received = 0
            loop_count = 0
            while tx_thread.is_alive():
                # Process any received messages
                while not response_queue.empty():
                    try:
                        response = response_queue.get_nowait()
                        messages_received += 1
                        print(f"Received ({messages_received}): '{response}'")
                        response_queue.task_done()
                    except:
                        break
                
                # Optional: Check thread status every 5 seconds (50 loops * 0.1s)
                loop_count += 1
                if loop_count % 50 == 0:
                    # Uncomment the next line if you want periodic thread status updates
                    # check_thread_status(tx_thread, rx_thread)
                    pass
                
                time.sleep(0.1)  # Check for messages every 100ms
            
            print("Data transmission completed.")
            
            # Signal RX thread to stop now that TX is done
            stop_event.set()
            
            # Give RX thread a moment to process any final incoming data
            time.sleep(0.2)
            
            # Process any remaining messages
            while not response_queue.empty():
                try:
                    response = response_queue.get_nowait()
                    messages_received += 1
                    print(f"Received ({messages_received}): '{response}'")
                    response_queue.task_done()
                except:
                    break
            
            # Wait for RX thread to properly finish
            print("Waiting for RX thread to terminate...")
            if rx_thread.is_alive():
                rx_thread.join(timeout=1.0)  # Wait up to 1 second
                if rx_thread.is_alive():
                    print("Warning: RX thread did not terminate cleanly")
                else:
                    print("RX Thread: Terminated cleanly")
            else:
                print("RX Thread: Already terminated")
            
            # Final check: Verify all threads are finished
            print("\n--- Thread Status Summary ---")
            print(f"TX Thread alive: {tx_thread.is_alive()}")
            print(f"RX Thread alive: {rx_thread.is_alive()}")
            
            all_threads_finished = not (tx_thread.is_alive() or rx_thread.is_alive())
            print(f"All threads finished: {all_threads_finished}")
            
            if all_threads_finished:
                print("All threads terminated successfully")
            else:
                print("Some threads are still running")

    except KeyboardInterrupt:
        # Program stops if press Ctrl+C in the terminal
        print("\nProgram stopped by user.")
    except serial.SerialException as e:
        print(f"\nSerial Port Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    
    finally:
        # Ensure all threads are signaled to stop (in case of exceptions)
        stop_event.set()
        
        print("\n--- Final Cleanup ---")
        
        # Wait for any remaining threads to finish with detailed status
        active_threads = []
        for thread_name, thread in [("RX", rx_thread), ("TX", tx_thread)]:
            if thread_name.lower() + '_thread' in locals() and thread.is_alive():
                print(f"Waiting for {thread_name} thread to finish...")
                thread.join(timeout=1.0)
                if thread.is_alive():
                    print(f"⚠️  {thread_name} thread still running after timeout")
                    active_threads.append(thread_name)
                else:
                    print(f"✅ {thread_name} thread finished")
        
        # Final thread status report
        if active_threads:
            print(f"Warning: {len(active_threads)} thread(s) still active: {', '.join(active_threads)}")
        else:
            print("All threads terminated successfully")
        
        # Close serial connection
        if ser_connection and ser_connection.is_open:
            ser_connection.close()
            print(f"Serial port {port_name} closed.")
        
        print("--- Cleanup Complete ---")
    

