# wifi_module.py
# -*- coding: utf-8 -*-
from machine import Pin, SPI
import time
import network
import json
import uasyncio as asyncio  # 添加异步支持

#常量與配置文件相關
from const_and_config import device_id, DEBUG, ssid, password, url_scheme, url_host, url_port, tapping_card_led_pin, winfi_led_pin
 
class WiFiCreator:
    def __init__(self):
        # 添加默认配置
        self.wifi_ssid = "WiFi001"          # default_ssid
        self.wifi_password = "abc12345"      # default_password
        
        # 启动时加载保存的配置
        try:
            with open("wifi_config.json") as f:
                config = json.load(f) 
                self.wifi_ssid = config['ssid']
                self.wifi_password = config['password']
                
                print(f"\nWiFiCreator Stucture Func: open wifi_config.json {self.wifi_ssid} {self.wifi_password}\n")
        except:
            print("\nNo saved configuration found(wifi_config.json), using default values\n")
             
        self.wlan = None  # 添加wlan实例变量
    
    async def connect_wifi(self):
        """异步连接WiFi，带重试机制"""
        attempt = 0
        max_attempts = 5
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\nWiFi connection attempt {attempt}/{max_attempts}\n")
            
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            
            # 如果已经连接，直接返回
            if self.wlan.isconnected():
                print("\nAlready connected to WiFi\n")
                return self.wlan
            
            # 确保有有效的SSID
            if not self.wifi_ssid:
                print("\nNo SSID configured\n")
                await asyncio.sleep(5)
                continue
            
            print(f"\nConnecting to: {self.wifi_ssid}\n")
            
            try:
                self.wlan.connect(self.wifi_ssid, self.wifi_password)
            except Exception as e:
                print(f"\nfunc::connect_wifi exception: Connection error: {e}\n")  
                
            # 无论是否异常，只要没连接成功就等待后继续
            print("Connection attempt failed, retrying...")
            
            await asyncio.sleep(2)
            
            print("Connection attempt do.......")
            
            
            # 嘗試5次後 180秒後等待连接 調試環境下 120秒
            timeout = 600 if DEBUG else 300 
            start_time = time.time()
            
            while not self.wlan.isconnected() and (time.time() - start_time) < timeout:
                status = self.wlan.status()
                if status == network.STAT_CONNECTING:
                    print(f"Connecting... {int(timeout - (time.time() - start_time))}s left")
                elif status == network.STAT_NO_AP_FOUND:
                    print("AP not found")
                    break
                elif status == network.STAT_WRONG_PASSWORD:
                    print("Wrong password")
                    break
                elif status == network.STAT_CONNECT_FAIL:
                    print("Connection failed")
                    break
                
                await asyncio.sleep(1)  #
                
                
            
            if self.wlan.isconnected():
                print("WiFi connected successfully!")
                print(f"IP: {self.wlan.ifconfig()[0]}")
                return self.wlan
            else:
                print(f"Connection attempt {attempt} failed")
                self.wlan.disconnect()
                self.wlan.active(False)
                await asyncio.sleep(3)
        
        print("\nAll connection attempts failed\n")
        return None
    
     
    # wifi是否连接
    async def isconnected(self):
        return self.wlan.isconnected() if self.wlan else False
         
    # 添加異步重新连接方法        
    async def reconnect(self):
        """异步重连"""
        if not self.wlan:
            print("No WLAN instance, cannot reconnect")
            return False
        
        print("Reconnecting to WiFi...")
        try:
            self.wlan.disconnect()
            await asyncio.sleep(1)
            self.wlan.connect(self.wifi_ssid, self.wifi_password)
            
            # 等待连接
            for _ in range(15):
                if self.wlan and self.wlan.isconnected():
                    return True
                await asyncio.sleep(1)
            
            return False
        except Exception as e:
            print(f"Reconnect error: {e}")
            return False
    
""" TEST

  
# start the wifi module test system
if __name__ == "__main__":
    # create a instance
    wiFiCreator = WiFiCreator() 
    
    async def test_connection():
        # 连接WiFi 
        wlan = await wiFiCreator.connect_wifi()
    
    asyncio.run(test_connection())
    
"""
   
