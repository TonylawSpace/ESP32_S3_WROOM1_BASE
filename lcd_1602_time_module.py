import uasyncio as asyncio
import LCD1602
import time


# 時間顯示模組 只顯示時間和月日 格式 row 0# 19:00:07 11-02
class DateTimeModule:
    def __init__(self, lcd, lcd_lock):
        self.lcd = lcd
        self.lcd_lock = lcd_lock
        asyncio.create_task(self.display_time())

    async def display_time(self):
        try:
            while True:
                # 获取锁
                async with self.lcd_lock:
                    # set the cursor to column 0, line 1
                    self.lcd.setCursor(0, 0)
                    # self.lcd.setCursor(1, 1) position测试
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


async def main():
    # 创建 LCD 对象
    lcd = LCD1602.LCD1602(16, 2)
    # 创建锁
    lcd_lock = asyncio.Lock()

    # 创建 DateTimeModule 实例
    date_time_module = DateTimeModule(lcd, lcd_lock)

    try:
        # 保持主协程运行
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Program stopped by user.")


if __name__ == "__main__":
    asyncio.run(main())