import time
import os
import wifi


database_url = os.getenv("database_url")
apikey = os.getenv("apikey")

def connect_to_wifi():

    ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    

    try:
        # Connect to the Wi-Fi network
        wifi.radio.connect(ssid, password)
    except OSError as e:
        print(f"OSError: {e}")
    print("Wifi Connected")

headers = {
  'apikey': apikey,
  'Content-Type': 'application/json'
}

motions = ('left', 'right', 'up', 'down')

def post_file(data):

    ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

    import adafruit_connection_manager
    import adafruit_requests
    import wifi

    try:
        # Connect to the Wi-Fi network
        wifi.radio.connect(ssid, password)
    except OSError as e:
        print(f"OSError: {e}")
    print("Wifi Connected")



    pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
    ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl_context)

    file = "["
    for pt, i in zip(data, range(len(data))):
        accel = pt[0]
        gyro = pt[1]
        orient = pt[2]
        
        data_pt = f'''{{ 
            "acc_x": {accel[0]},
            "acc_y": {accel[1]},
            "acc_z": {accel[2]},
            "gyro_x": {gyro[0]},
            "gyro_y": {gyro[1]},
            "gyro_z": {gyro[2]},
            "orient_x": "{orient[0]}",
            "orient_y": {orient[1]},
            "orient_z": {orient[2]}
        }},'''
        file = file + data_pt
    
    file = file[:-1]+']'
    response = requests.post(f"{database_url}/rest/v1/path", data=file, headers=headers)

    response.close()

def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f"Countdown: {i}")
        time.sleep(1)
    print("Go!")