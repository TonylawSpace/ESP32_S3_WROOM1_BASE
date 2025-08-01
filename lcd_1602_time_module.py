# lcd_1602_time_module.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio
import LCD1602
import time

# lcd_lock = asyncio.Lock()
# 時間顯示模組 只顯示時間和月日 格式 row 0# 19:00:07 11-02
class DateTimeModule:
    def __init__(self,lcd):
        self.wifi_current_status = False
        self.lcd = lcd
        self.lcd_lock = asyncio.Lock()
        asyncio.create_task(self.display_time())

    async def display_time0(self):
        """
        如果设备（如 ESP32、ESP8266 等开发板）未进行时区配置，time.localtime() 通常默认返回 UTC 时间（世界协调时间）
        """
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
    
    async def display_time(self):
        """
        如果设备（如 ESP32、ESP8266 等开发板）未进行时区配置，time.localtime()  手動調整為本地時間
        """
        try:
            while True:
                # 获取锁
                async with self.lcd_lock:
                    # 设置光标到第0行第0列
                    self.lcd.setCursor(0, 0)
                    
                    # 获取当前时间（UTC时间）
                    utc_time = list(time.localtime())  # 格式: [年, 月, 日, 时, 分, 秒, 周几, 年第几天]
                    
                    # 转换为本地时间（假设本地时区为UTC+8，可根据实际情况调整偏移量）
                    timezone_offset = 8  # 时区偏移小时数（例如UTC+8）
                    local_hour = utc_time[3] + timezone_offset
                    
                    # 处理跨天情况
                    if local_hour >= 24:
                        local_hour -= 24
                        # 日期加1
                        # 这里简化处理，实际可能需要考虑月份天数和闰年
                        utc_time[2] += 1
                    elif local_hour < 0:
                        local_hour += 24
                        utc_time[2] -= 1
                    
                    # 构造本地时间列表
                    local_time = utc_time.copy()
                    local_time[3] = local_hour  # 更新小时
                    
                    # 格式化时间（补零）
                    local_time = ["{:0>2}".format(str(i)) for i in local_time]
                    
                    # 显示格式: 时:分:秒 月-日
                    self.lcd.printout(f"{local_time[3]}:{local_time[4]}:{local_time[5]}  {local_time[1]}-{local_time[2]}")

                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            # 清理操作
            async with self.lcd_lock:
                self.lcd.clear()
             
    # update wifi status            
    async def update_wifi_current_status(self, status: bool):
            """更新WIFI状态"""
            self.wifi_current_status = status
            print("update_wifi_current_status------------")
    
    # 顯示wifi信號
    async def display_wifi_signal(self):
            
            # print("display_wifi_signal try------------")
            try:
                while True:
                    # 获取锁
                    async with self.lcd_lock:
                        # print("display_wifi_signal while------------")
                        # 设置光标位置到第2行第16列(注意：LCD通常从0开始计数)
                        self.lcd.setCursor(15, 1) 
                        # 显示wifi信号图标
                        if self.wifi_current_status:
                            self.lcd.printout("*") 
                        else:
                            self.lcd.printout("/")
                            await asyncio.sleep(0.3)
                            self.lcd.setCursor(15, 1) 
                            self.lcd.printout("-")
                            await asyncio.sleep(0.3)
                            self.lcd.setCursor(15, 1) 
                            self.lcd.printout("|")
                            await asyncio.sleep(0.3)
                            self.lcd.setCursor(15, 1) 
                            self.lcd.printout(" ")  # 清空此格
                            
                        await asyncio.sleep(2)  # 异步等待
                        
                       
                        # print("func:DateTimeModule::display_wifi_signal------------") 
                    
            except KeyboardInterrupt:
                self.lcd.clear() 
            
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