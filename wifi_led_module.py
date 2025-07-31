import uasyncio as asyncio
from machine import Pin
from time import sleep

#常量與配置文件相關
from  const_and_config import device_id, DEBUG, ssid, password, url_scheme, url_host, tapping_card_led_pin, winfi_led_pin
 
"""
WIFI信號燈
功能與用法說明：
ESP32-S2 LCD 使用引腳 PIN1#（GP2）
正常：每30秒閃一秒
断线：每1秒闪一次
"""
# 全局锁
lock_winfi_led = asyncio.Lock()

# WIFI信號燈
class WifiIndicator:
    def __init__(self, wifi_current_status: bool, led_pin_num_winfi: int = 2):  # ESP32-S2 LCD 使用引腳 PIN1#（GP2）
        self.led_wifi_singal = Pin(winfi_led_pin, Pin.OUT) #Pin(led_pin_num_winfi, Pin.OUT)  # 該從配置文件中獲得wifi燈的引腳
        self.wifi_current_status = wifi_current_status
        self.led_pin_num_winfi = led_pin_num_winfi  # 存储引脚号供后续使用
        self.led_wifi_singal.off()  # 初始状态为关闭  <-- 添加这行

    async def blink(self):  # 异步闪烁任务
        try:
            while True:
                async with lock_winfi_led:  # 安全訪問LED
                    # 亮灯
                    self.led_wifi_singal.on()
                    print(f"LED WiFi Pin{self.led_pin_num_winfi} ON")
                    
                    # Print wifi status
                    # print(f"WIFI STAUS: {self.wifi_current_status}")
                    # 根据状态设置延时
                    if self.wifi_current_status: 
                        # 根据 DEBUG 常量选择休眠时间
                        if DEBUG:
                            await asyncio.sleep(10)  # 调试环境下延长休眠时间
                        else:
                            await asyncio.sleep(30)   # 生产环境下使用正常休眠时间 
                    else:
                        await asyncio.sleep(0.2)
                        print("[WifiIndicator] WIFI disconnected!")
                    
                    # 灭灯
                    self.led_wifi_singal.off()
                    print(f"LED WiFi Pin{self.led_pin_num_winfi} OFF")
                    await asyncio.sleep(2)  # 异步等待
                    
        except KeyboardInterrupt:
            self.led_wifi_singal.off()
            print("Program stopped")
            
    async def update_wifi_current_status(self, status: bool):
        """更新WIFI状态"""
        self.wifi_current_status = status
        
    async def led_off(self):
        # 灭灯
        self.led_wifi_singal.off()

"""
去掉引號進行測試

# 使用示例
async def main():
    wifi_led = WifiIndicator(wifi_current_status=True)
    asyncio.create_task(wifi_led.blink())  # 启动异步任务
    await asyncio.sleep(30)  # 30秒後交出控制权
    wifi_led.led_off() # 最後熄燈
# 启动事件循环
try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
"""