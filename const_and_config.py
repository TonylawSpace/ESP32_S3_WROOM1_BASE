# 常量 與 配置相關
# const_and_config.py
# -*- coding: utf-8 -*-
from machine import Pin
import time 
import binascii
import ujson as json

# DEBUG 總開關
# 在文件开头定义 DEBUG 常量 根據環境設置參數的值的大小
DEBUG = True  # 调试时设为 True，发布时设为 False


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
 
try:
    with open('wifi_config.json', 'r', encoding='utf-8') as f:  # 使用 'r' 模式读取，并指定编码
        config = json.load(f) 
        ssid = config['ssid']
        password = config['password']
        url_scheme = config['url_scheme']
        url_host = config['url_host']
        print(f"\nssid={ssid}; password={password}; url_scheme={url_scheme}; url_host={url_host}\n")
             
except FileNotFoundError:  # 注意这里的缩进，与try保持一致
    print(f"Error: no file wifi_config.json") 
except Exception as e:
    print(f"Error reading wifi_config.json file: {e}")