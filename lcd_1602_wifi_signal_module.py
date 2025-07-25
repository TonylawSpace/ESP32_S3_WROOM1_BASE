# lcd_1602_wifi_signal_module.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio
import LCD1602
import time

# 顯示第二行最後一位為WIFI信號
class WifiSignalModule:
    def __init__(self): 
        
        # 这里的状态只是初始默认值
        self.wifi_current_status = False
         
        # 创建LCD对象，指定I2C地址和显示大小（例如0x27是常见的I2C地址）
        self.lcd = LCD1602.LCD1602(16, 2) 
        self.lcd_lock = asyncio.Lock()

    async def update_wifi_current_status(self, status: bool):
        """更新WIFI状态"""
        self.wifi_current_status = status
        
    async def display_wifi_signal(self):
        try:
            while True:
                # 获取锁
                async with self.lcd_lock:
                    
                    # 设置光标位置到第2行第16列(注意：LCD通常从0开始计数)
                    self.lcd.setCursor(16, 1)  # 修正：使用self.lcd
                    # 显示wifi信号图标
                    if self.wifi_current_status:
                        self.lcd.printout("*")  # 修正：使用self.lcd
                    else:
                        self.lcd.printout("/")  # 修正：使用self.lcd
                        
                    await asyncio.sleep(2)  # 异步等待
                    
                    self.lcd.setCursor(16, 1)
                    # self.lcd.autoscroll()
                    self.lcd.printout(" ")  # 清空此格
                     
                
        except KeyboardInterrupt:
            self.lcd.clear()  # 修正：使用self.lcd 

"""TEST"""
# 启动系统
if __name__ == "__main__":
    wifiSignalModule = WifiSignalModule()  # 修正：变量名使用小写开头
    wifiSignalModule.display_wifi_signal()  # 调用方法显示WiFi信号