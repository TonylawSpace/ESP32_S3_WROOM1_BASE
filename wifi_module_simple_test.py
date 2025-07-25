import network
import time

print("WiFi connection test")

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)
wlan.active(True)
time.sleep(1)

print("Connecting to WiFi...")
wlan.connect('WiFi001', 'abc12345')

timeout = 10
while timeout > 0:
    status = wlan.status()
    print(f"Status: {status}, Connected: {wlan.isconnected()}")
    if wlan.isconnected():
        print("Connected! IP:", wlan.ifconfig()[0])
        break
    time.sleep(1)
    timeout -= 1

if not wlan.isconnected():
    print("Connection failed")