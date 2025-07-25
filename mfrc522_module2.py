from machine import Pin, SPI
import time
from mfrc522 import MFRC522


## **Esp32 S3接线：**

# RDID-RC522的SDA -> esp32-s3的引脚10
# 
# RDID-RC522的SCK -> esp32-s3的引脚12
# 
# RDID-RC522的MOSI -> esp32-s3的引脚11
# 
# RDID-RC522的MISO -> esp32-s3的引脚13
# 
# RDID-RC522的GUN -> esp32-s3的引脚GUN
# 
# RDID-RC522的RST -> esp32-s3的引脚46
# 
# RDID-RC522的3.3V -> esp32-s3的引脚3.3V

# ESP32-S3 优化引脚配置
sda = Pin(10, Pin.OUT)   # 片选
sck = Pin(12, Pin.OUT)   # HSPI SCK
mosi = Pin(11, Pin.OUT)  # HSPI MOSI
miso = Pin(13, Pin.IN)   # HSPI MISO (关键修改：避免BOOT冲突)
rst = Pin(46, Pin.OUT)   # 复位

# 初始化SPI1 (HSPI) - 提高波特率
spi = SPI(1,
          baudrate=1000000,  # 5MHz
          polarity=0,
          phase=0,
          sck=sck,
          mosi=mosi,
          miso=miso)

class RFIDReader:
    def __init__(self, spi, rst, sda):
        # 保存引脚对象
        self.rst = rst
        self.sda = sda
        self.spi = spi
        
        # 创建MFRC522实例
        self.rfid = MFRC522(spi, rst, sda)
        self.last_uid = None
        print("RFID Reader initialized")
        
        # 执行硬件复位测试
        self.hardware_reset()
    
    def hardware_reset(self):
        """执行硬件复位序列"""
        print("执行硬件复位...")
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(50)
        print("复位完成")
    
    def read_card(self):
        """主读卡循环"""
        print("等待卡片靠近...")
        error_count = 0
        while True:
            # 尝试多种请求类型提高兼容性
            for req_type in [self.rfid.REQIDL, 0x26, 0x52]:
                try:
                    stat, bits = self.rfid.request(req_type)
                    #print(f"请求类型: 0x{req_type:02X}, 状态: {stat}, 位长度: {bits}")
                    
                    if stat == self.rfid.OK:
                        # 防冲突获取UID
                        stat, raw_uid = self.rfid.anticoll()
                        
                        if stat == self.rfid.OK:
                            # 格式化UID
                            uid = "0x%02X%02X%02X%02X" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                            
                            # 避免重复读取同一张卡
                            if uid != self.last_uid:
                                print(f"检测到卡片! UID: {uid}")
                                self.last_uid = uid
                                
                                # 验证卡片权限
                                if self.check_access(uid):
                                    print("访问已授权")
                                    # 这里添加开门等操作
                                else:
                                    print("未授权卡片")
                except Exception as e:
                    error_count += 1
                    print(f"读卡错误 #{error_count}: {e}")
                    if error_count > 10:
                        print("过多错误，尝试硬件复位...")
                        self.hardware_reset()
                        error_count = 0
            
            time.sleep_ms(100)  # 适当延迟
    
    def check_access(self, uid):
        """卡片访问权限检查"""
        # 示例授权卡片列表
        authorized_cards = {
            "0x5A3B8D7E": "管理员",
            "0xC4F21A9B": "普通用户"
        }
        return uid in authorized_cards

# 启动系统
if __name__ == "__main__":
    print("启动RFID门禁系统")
    # 创建RFIDReader实例，传入spi, rst, sda
    reader = RFIDReader(spi, rst, sda)
    reader.read_card()