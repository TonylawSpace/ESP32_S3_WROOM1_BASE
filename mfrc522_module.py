from machine import Pin, SPI
import uasyncio as asyncio
from os import uname
import LCD1602
import time
from mfrc522 import MFRC522

#  NXP RC522 射频模块应用
#  ref https://github.com/gwvsol/ESP32-RFID-RC522 

# NFC门禁系统：通过读取员工或访客携带的 RFID 卡片的 UID，

class MfrcUtility:
    counter = 0  # 类属性，用于计数

    def __init__(self, spi, rst, cs):
        self.rfid = MFRC522(spi, rst, cs)

    def do_read_nfc(self):
        result = self.rfid.read_card()
        self.counter += 1  # 通过 self 访问类属性并进行修改
        if result is not None:
            uid, card_data = result
            print(f"Card detected. {self.counter}")
            print(f"Read card UID: {uid}")
            print(f"Card data: {card_data}")
            return uid, card_data
        else:
            print(f"No card detected. {self.counter}")
            return None

# 启动系统
if __name__ == "__main__":
    print(uname()[0])
    # 初始化SPI接口，指定mosi、miso、sck引脚
    spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(16), miso=Pin(17))
    # 初始化引脚
    rst = Pin(15, Pin.OUT)
    cs = Pin(19, Pin.OUT)  # SDA（数据接口）实际上就相当于CS引脚。在 SPI 通信里，SDA有时候也会被当作CS来使用。

    utility = MfrcUtility(spi, rst, cs)
    while True:
        utility.do_read_nfc()
        time.sleep(1)