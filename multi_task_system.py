# multi_task_system.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio
import network
from machine import UART, Pin, I2C
import time
import gc
import os
import ubinascii
import LCD1602
from wifi_module import WiFiCreator 
from wifi_led_module import WifiIndicator  # 导入WIFI 指示燈模块
from config_server import ConfigServer  # 导入AP熱點模块
from uart_m4255_module import UartM4255NfcModule # 导入UART拍卡M4255模块
from lcd_1602_wifi_signal_module import WifiSignalModule  # 导入WifiSignalModule for lcd signal模块
from lcd_1602_time_module import DateTimeModule    # 导入DateTimeModule模块

# 在文件开头定义 DEBUG 常量 根據環境設置參數的值的大小
DEBUG = True  # 调试时设为 True，发布时设为 False

# 创建全局锁
multi_task_lock = asyncio.Lock()
counter = 0

class MultiTaskSystem:
    def __init__(self):
        # 創建WIFI 
        self.wifiCreator = WiFiCreator()
        # 初始化
        self.wlan = None
        self.current_wifi_status = False
        
        # AP實例
        self.ap_task = None  # 添加AP任务引用
        self.config_server = ConfigServer()
        self.config_server.stop() # 初始是停止AP
        self.current_ap_status = False
         
        
        # self.led = machine.Pin(12, machine.Pin.OUT)
        self.sensor_counter = 0
        # self.resource_timer = 0 XXXXXX
        self.tasks = []
        
        # Led WifiIndicator 初始化WIFI闪灯指示器
        self.wifiIndicator = WifiIndicator(wifi_current_status=False)
          
        # 拍卡设备串口初始化 Card scanning device serial port initialization
        uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=Pin(18), tx=Pin(17))
        self.uart = uart1
         
        # 创建LCD对象，指定I2C地址和显示大小（例如0x27是常见的I2C地址） 
        self.lcd = LCD1602.LCD1602(16, 2) 
        
        # 拍卡设备实例 Card tapping device instance 
        self.uartM4255NfcModule = UartM4255NfcModule(self.uart, self.lcd) 
        
        # wifi lcd singal
        self.wifiSignalModule = WifiSignalModule()
        # Time LCD
        self.dateTimeModule = DateTimeModule(self.lcd)
         
    async def wifi_manager_info(self):
        """管理WiFi连接和状态监控"""
        
        print(f"\nfunc::wifi_manager_info [Manage WiFi connections and status monitoring]\n")
        
        # 初始连接
        try:
            self.wlan = await self.wifiCreator.connect_wifi()
            print(f"\nfself.wlan = [{self.wlan}]\n")
            self.current_wifi_status = self.wlan.isconnected() if self.wlan else False
        except Exception as e:
            print(f"Initial WiFi connection failed: {e}")
            self.current_wifi_status = False
        
        ap_start_attempted = False
        
        while True:
            try:
                # 安全地获取当前状态
                current_status = self.wlan.isconnected() if self.wlan else False
                self.current_wifi_status = current_status
                print(f"WIFI STATUS: {current_status}")
                
                if current_status:
                    ip = self.wlan.ifconfig()[0]
                    print(f"WiFi connected! IP: {ip}")
                    
                    # 停止AP如果正在运行
                    if self.ap_task:
                        print("Stopping AP mode...")
                        self.config_server.stop()
                        self.ap_task.cancel()
                        self.ap_task = None
                        self.current_ap_status = False
                        ap_start_attempted = False
                else:
                    print("WiFi disconnected. Attempting to reconnect...")
                    try:
                        # 尝试重新连接
                        reconnect_success = await self.wifiCreator.reconnect()
                        
                        # 安全地更新状态
                        if self.wlan:
                            self.current_wifi_status = self.wlan.isconnected()
                        else:
                            self.current_wifi_status = False
                    except Exception as e:
                        print(f"Reconnect failed: {e}")
                        self.current_wifi_status = False
                    
                    # 当WIFI连接失败且未尝试启动AP时
                    if not self.current_wifi_status and not ap_start_attempted:
                        print("Starting AP mode for configuration...")
                        try:
                            self.ap_task = asyncio.create_task(self.start_ap())
                            ap_start_attempted = True
                        except Exception as e:
                            print(f"Failed to start AP task: {e}")
                
                # 更新Led WifiIndicator的状态
                if self.wifiIndicator:
                    print("wifiIndicator.update_wifi_current_status")
                    await self.wifiIndicator.update_wifi_current_status(self.current_wifi_status)
                
                 # 更新LCD WifiSignalModule的状态
                if self.wifiSignalModule:
                    print("wifiSignalModule.update_wifi_current_status")
                    await self.wifiSignalModule.update_wifi_current_status(self.current_wifi_status)
                     
                     
                await asyncio.sleep(5 if DEBUG else 30)
            
            except Exception as e:
                print(f"Error in wifi_manager_info: {e}")
                await asyncio.sleep(10)
    
    async def start_ap(self):
        """启动AP模式"""
        try:
            self.current_ap_status = True
            print("AP mode starting...")
            await self.config_server.start_async()
        except Exception as e:
            print(f"Failed to start AP: {e}")
            self.current_ap_status = False
            self.config_server.stop()
            
    # wifi 指示燈 弃用 Depriate
    async def led_indicator(self):
        """LED状态指示器"""
        self.wifiIndicator = WifiIndicator(self.current_wifi_status)
        asyncio.create_task(self.wifiIndicator.blink())  # 启动异步任务
        
    async def sensor_reader(self):
        """模拟传感器数据读取"""
        while True:
            self.sensor_counter += 1
            # 这里读取实际传感器数据
            print(f"模拟传感器数据读取 Sensor reading #{self.sensor_counter}")
            await asyncio.sleep(2)
 
    async def resource_monitor(self):
        """系统资源监控"""
        while True:
            free_mem = gc.mem_free()
            total_mem = gc.mem_alloc() + free_mem
            fs_stat = os.statvfs('/')
            free_disk = fs_stat[0] * fs_stat[3]  # 块大小 * 空闲块数

            print(f"Memory: {free_mem}/{total_mem} bytes free")
            print(f"Storage: {free_disk} bytes free")

            # 自动垃圾回收
            if free_mem < 20000:  # 当内存低于20KB时
                gc.collect()
                print("Performed garbage collection")

            await asyncio.sleep(240) # 6分鐘釋放操作一次
 
    async def main(self):
        """主协程"""
        # 创建任务
        self.tasks = [
            asyncio.create_task(self.wifi_manager_info()),
            # asyncio.create_task(self.sensor_reader()),
            asyncio.create_task(self.uartM4255NfcModule.uart_card_listen_and_return()), 
            asyncio.create_task(self.dateTimeModule.display_time()),
            asyncio.create_task(self.wifiSignalModule.display_wifi_signal()),
            asyncio.create_task(self.wifiIndicator.blink()), 
            asyncio.create_task(self.resource_monitor()),
            asyncio.create_task(self.Counter())
            ]

        # 运行所有任务
        await asyncio.gather(*self.tasks)

    def run(self):
        """启动系统"""
        try:
            asyncio.run(self.main())
        except KeyboardInterrupt:
            print("System stopped by user")
        except Exception as e:
            print(f"System error: {e}")
            # 重启系统
            print("Rebooting...")
            machine.reset()
        finally:
            # 清理资源
            for task in self.tasks:
                task.cancel()
            asyncio.new_event_loop()

    async def Counter(self):
        global counter
        while True:
            # 获取锁
            async with multi_task_lock:
                # 关键代码区域
                counter += 1
                print(f"Counter: {counter}")
            await asyncio.sleep(60)  # 接下來的 3秒不使用CPU,释放CPU，允许其他协程运行
        
"""
TEST
# 启动系统
if __name__ == "__main__":
    
    # 清理内存
    gc.collect()
    print(f"Free memory: {gc.mem_free()} bytes")
    
    # 获取设备唯一ID用于AP名称
    # device_id = ubinascii.hexlify(machine.unique_id()).decode()[-4:]# 4位
    device_id = ubinascii.hexlify(machine.unique_id()).decode()
    print(f"device_id:{device_id}")
    
    # ap_name = f"ESP32-Config-{device_id}"
    ap_name = "ESP32-Config"
    
    system = MultiTaskSystem()
    system.run()
"""