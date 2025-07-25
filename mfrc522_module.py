from machine import Pin
import uasyncio as asyncio
from os import uname
import LCD1602
import time
# from mfrc5cc import MFRC522

#  NXP RC522 射频模块应用
#  ref https://github.com/gwvsol/ESP32-RFID-RC522 

# NFC门禁系统：通过读取员工或访客携带的 RFID 卡片的 UID，


# 创建对应的引脚对象
sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
sda = Pin(5, Pin.Out)

# 創建 SPI對象
spi = SPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, mosio=mosio)

class MfrcUtility:
    
    def read_id():
        # 1. 创建RFID操作对象
        rfid = MFRC522(spi, sda)

        # 2. 循环读取数据
        while True:

        # 3.复位应答
        stat, tag_type = rfid.request(rfid.REQIDL)
        if stat == rfid.OK:
        #4.防冲突检测,提取玉d号
        stat, raw_uid = rfid.anticoll()
        if stat == rfid.OK:
        _id= "0x%02xX02x%02xX02x"%(raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
        print("rfid |/fid:", id, raw_uid)

        sleep_ms(500)

        if name == " main ":
        read_id()

    def do_read():

        if uname()[0] == 'WiPy':
            rdr = mfrc522.MFRC522("GP14", "GP16", "GP15", "GP22", "GP17")
        elif uname()[0] == 'esp32':
            rdr = mfrc522.MFRC522(0, 2, 4, 5, 14)
        else:
            raise RuntimeError("Unsupported platform")

        print("")
        print("Place card before reader to read from address 0x08")
        print("")

        try:
            while True:
            

                
                (stat, tag_type) = rdr.request(rdr.REQIDL)

                if stat == rdr.OK:

                    (stat, raw_uid) = rdr.anticoll()

                    if stat == rdr.OK:
                        print("New card detected")
                        print("  - tag type: 0x%02x" % tag_type)
                        print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                        print("")
                        

                        if rdr.select_tag(raw_uid) == rdr.OK:

                            key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                            if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
                                print("Address 8 data: %s" % rdr.read(8))
                                rdr.stop_crypto1()
                            else:
                                print("Authentication error")
                        else:
                            print("Failed to select tag")
                            
                        


        except KeyboardInterrupt:
            print("Bye")


# 启动系统
if __name__ == "__main__":
     
     print(uname()[0])