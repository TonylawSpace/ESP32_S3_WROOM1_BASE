# 常量 與 配置相關
# const_and_config.py
# -*- coding: utf-8 -*-
import sys
from machine import Pin
import time
import machine 
import binascii
import ujson as json
import ubinascii

# 获取设备唯一ID 提供雲端登記
device_id = ubinascii.hexlify(machine.unique_id()).decode()
print(f"\ndevice_id={device_id}\n")

# DEBUG 總開關
# 在文件开头定义 DEBUG 常量 根據環境設置參數的值的大小
DEBUG = True  # 调试时设为 True，发布时设为 False
 
# API PATH 雲主機POST PATH ,默認是語言版本設定為英文 Language=en-US
api_post_path = "en-US/Admin/DeviceManage/CardDeviceSimplifiedEntry"

# 拍卡指示燈 RGB_LED GPIO038
tapping_card_led_pin = 38 

# WIFI信號燈 RGB_LED GPIO02
winfi_led_pin = 2

# 讀取配置文件的配置參數
# ssid password url_scheme url_host

ssid = "WiFi001"
password = "abc12345"
url_scheme = "http"
url_host = "192.168.1.9"
url_port = 8080 # API 雲主機端口

try:
    with open('wifi_config.json', 'r', encoding='utf-8') as f:  # 使用 'r' 模式读取，并指定编码
        config = json.load(f) 
        ssid = config['ssid']
        password = config['password']
        url_scheme = config['url_scheme']
        url_host = config['url_host']
        url_port = config['url_port']
        print(f"\nssid={ssid}; password={password}; url_scheme={url_scheme}; url_host={url_host}; url_port={url_port}\n")
             
except OSError as e:
    if e.errno == 2:  # File not found error code
        print("Error: no file wifi_config.json")
    else:
        print(f"Error reading wifi_config.json file: {e}")
except Exception as e:
    print(f"Error reading wifi_config.json file: {e}")