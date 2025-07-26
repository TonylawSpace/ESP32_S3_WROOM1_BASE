# lcd_1602_time_module.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio
import LCD1602
import time

# lcd_lock = asyncio.Lock()
# 時間顯示模組 只顯示時間和月日 格式 row 0# 19:00:07 11-02
class DateTimeModule:
    def __init__(self,lcd):
        self.lcd = lcd
        self.lcd_lock = asyncio.Lock()
        asyncio.create_task(self.display_time())

    async def display_time(self):
        try:
            while True:
                # 获取锁
                async with self.lcd_lock:
                    # set the cursor to column 0, line 1
                    self.lcd.setCursor(0, 0)
                    # print the number of seconds since reset:
                    T = list(time.localtime())
                    T[6] += 1
                    T = ["{:0>2}".format(str(i)) for i in T]
                    self.lcd.printout(T[3] + ":" + T[4] + ":" + T[5] + ' ' + ' ' + T[1] + '-' + T[2])

                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            # 获取锁以确保安全清理
            async with self.lcd_lock:
                self.lcd.clear()
                
    # update wifi status            
    async def update_wifi_current_status(self, status: bool):
            """更新WIFI状态"""
            self.wifi_current_status = status
            print("update_wifi_current_status------------")
    
    # 顯示wifi信號
    async def display_wifi_signal(self):
            
            print("display_wifi_signal try------------")
            try:
                while True:
                    # 获取锁
                    async with self.lcd_lock:
                        print("display_wifi_signal while------------")
                        # 设置光标位置到第2行第16列(注意：LCD通常从0开始计数)
                        self.lcd.setCursor(15, 1)  # 修正：使用self.lcd
                        # 显示wifi信号图标
                        if self.wifi_current_status:
                            self.lcd.printout("*")  # 修正：使用self.lcd
                        else:
                            self.lcd.printout("/")  # 修正：使用self.lcd
                            
                        await asyncio.sleep(2)  # 异步等待
                        
                        self.lcd.setCursor(15, 1)
                        # self.lcd.autoscroll()
                        self.lcd.printout(" ")  # 清空此格
                        print("display_wifi_signal------------") 
                    
            except KeyboardInterrupt:
                self.lcd.clear()  # 修正：使用self.lcd
            
# async def main():
#     # 创建 LCD 对象
#     lcd = LCD1602.LCD1602(16, 2)
#     # 创建锁
#     lcd_lock = asyncio.Lock()
# 
#     # 创建 DateTimeModule 实例
#     date_time_module = DateTimeModule(lcd, lcd_lock)
# 
#     try:
#         # 保持主协程运行
#         while True:
#             await asyncio.sleep(1)
#     except KeyboardInterrupt:
#         print("Program stopped by user.")
# 
# 
# if __name__ == "__main__":
#     asyncio.run(main())