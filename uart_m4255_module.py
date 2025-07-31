# uart_m4255_module.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio
from machine import UART, Pin
import time
import binascii
import LCD1602
from cloud_module import CloudModule
#常量與配置文件相關
from const_and_config import device_id, DEBUG, ssid, password, url_scheme, url_host, tapping_card_led_pin, winfi_led_pin

uart_lcd_lock = asyncio.Lock()
# tapping_card_led_pin = 38 # 拍卡指示燈 RGB_LED GPIO038 改在 const_and_config.py 定义 
tapping_card_led_lock = asyncio.Lock() # 拍卡指示燈線程鎖

class UartM4255NfcModule:
    def __init__(self, uart,lcd):
        
        print(f"\nUartM4255NfcModule initialized with arguments: {uart}\n")
        
        if uart is not None:
            self.uart = uart
        else:
            # 当没有传入uart实例时，创建默认的UART1
            uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=Pin(18), tx=Pin(17))
            self.uart = uart1
            
        if lcd is not None:
            self.lcd = lcd
        else:
            self.lcd = LCD1602.LCD1602(16, 2)
            
        # 拍卡指示灯
        self.tapping_card_led = Pin(tapping_card_led_pin, Pin.OUT)
        self.tapping_card_led.off()  # 初始状态为关闭  
        
    def uart_to_card_number(self, raw_data, card_number_start=7, card_number_length=4, byte_order='big'):
        """
        从UART原始字节数据提取卡号（十进制）
        
        参数:
            raw_data: bytes对象 - UART原始数据
            card_number_start: int - 卡号起始字节位置 (默认7)
            card_number_length: int - 卡号长度（字节数，默认4)
            byte_order: str - 字节顺序 ('big' 或 'little'，默认大端序)
        
        返回:
            int: 十进制卡号 (提取失败返回None)
        """
        # 1. 输入验证
        if not isinstance(raw_data, bytes) or len(raw_data) == 0:
            print("Error: Invalid input data")
            return None
        
        # 2. 计算卡号结束位置
        end_pos = card_number_start + card_number_length
        
        # 3. 检查数据长度是否足够
        if len(raw_data) < end_pos:
            print(f"\nError: insufficient data length (needed at least {end_pos} bytes, actual {len(raw_data)} bytes)\n")
            return None
        
        try:
            # 显示原始HEX数据
            hex_str = binascii.hexlify(raw_data).decode("utf-8").upper()
            print(f"\nRaw HEX Data: {hex_str}\n")
            
            # 4. 提取卡号字节段
            card_bytes = raw_data[card_number_start:end_pos]
            
            # 5. 转换为整数
            card_number = int.from_bytes(card_bytes, byte_order)
            return card_number
        
        except Exception as e:
            print(f"\nCard number retrieval failed:\n")
            print(f"Card number retrieval failed: {str(e)}")
            return None
         
    # LCD 顯示拍卡號碼
    async def display_card_number(self, card_number):
        try:
            async with uart_lcd_lock:
                print("\n-------------------------------------------")
                print(f"func::display_card_number: {card_number}")
                print("-------------------------------------------\n")
                
                # 显示卡号
                self.lcd.setCursor(0, 1)
                self.lcd.printout(" " * 16)  # 清空第二行
                self.lcd.setCursor(0, 1)
                self.lcd.printout(f"Card:{card_number}")
                 
                # 2 秒後 清空卡號保護隱私 
                await asyncio.sleep(2)  # 修正：添加await
                
                self.lcd.setCursor(0, 1)  # 清空第二行
                self.lcd.printout(" " * 16) 
                
                    
        except KeyboardInterrupt:
            self.lcd.clear()
        except Exception as e:
            print(f"\nError in display_card_number: {e}\n")
                       
            
    async def uart_card_listen_and_return(self):
        """
            监听UART并返回检测到的卡号
            Monitor UART and return detected card number
        """
        
        print("\n拍卡器监听模组已启动...\nThe card reader monitoring module has been activated...\n")
        print("请将卡片靠近读卡器\nPut the card close to the reader\n")

        last_card_id = None
        last_detect_time = 0
        
        try:
            while True:
                # 检查是否有可用数据
                if self.uart.any():
                    bytes_available = self.uart.any()
                    print(f"\n{bytes_available} Bytes Available\n")
                    
                    # 读取所有可用数据
                    data = self.uart.read()
                    
                    if data:
                        print("\n原始数据/Raw data:", data)
                        
                        # 解析卡号
                        card_id = self.uart_to_card_number(data)
                        
                        if card_id is not None:
                            # 防重复读取机制
                            current_time = time.ticks_ms()
                            if card_id != last_card_id or time.ticks_diff(current_time, last_detect_time) > 2000:
                                print(f"\n检测到卡号/Card number detected: {card_id}\n")
                                last_card_id = card_id
                                last_detect_time = current_time
                                
                                # 显示card number
                                await self.display_card_number(card_id)
                                
                                
                                
                                cloudModule = CloudModule()
                                is_valid_card = await cloudModule.post_validate(card_id)
                                if is_valid_card:
                                    print(f"\nSUCCESS! IT IS A VALID REGISTED CARD: {card_id}\n")
                                    # 在此添加业务逻辑
                                    print("\n")
                                    print("-----------------------------------------------------------------------------------------------------")
                                    print(f"在此添加业务逻辑（如存储卡号、控制继电器等）: {card_id}")
                                    print(f"Add business logic here (such as storage card number, control relay, etc.): {card_id}")
                                    print("-----------------------------------------------------------------------------------------------------")
                                    print("\n")
                                else:
                                    print(f"\nFAIL! IT IS A INVALID CARD OR NOT A REGISTED CARD: {card_id}\n")
                                    
                                # 拍卡指示燈業務
                                async with tapping_card_led_lock:
                                    self.tapping_card_led.on()
                                    print(f"Tapping Card Led Pin{tapping_card_led_pin} On")
                                    await asyncio.sleep(1)
                                    self.tapping_card_led.off()
                                    print(f"Tapping Card Led Pin{tapping_card_led_pin} Off")
                        
                        # 短暂延时防止重复读取
                        await asyncio.sleep(0.5)  
                
                # 短暂延时减少CPU负载
                await asyncio.sleep(0.5)  # sleep参数是秒而不是毫秒
        
        except KeyboardInterrupt:
            print("\n[异常] 函数::uart_card_listen_and_return 已终止!!!")
            print("[Exception] Function::uart_card_listen_and_return has terminated!!!\n")
            return None

"""

async def test_UartM4255NfcModule():
    print("开始")
    
    # 配置UART1：RX=GPIO18（蓝色线）对应M4255-NFC硬件针口TX
    # TX=GPIO17（紫色线）对应M4255-NFC硬件针口RX
    uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=Pin(18), tx=Pin(17))
    lcd1 = LCD1602.LCD1602(16, 2)
    uartM4255NfcModule = UartM4255NfcModule(uart1,lcd1) 
    await uartM4255NfcModule.uart_card_listen_and_return()  # 修正：添加await
    
    await asyncio.sleep(300)  # 真正等待300秒
    print("300秒后停止")  # 这行代码会在300秒后才运行
    
# 启动系统
if __name__ == "__main__":
    # 修正：添加括号调用函数，获取协程对象
    asyncio.create_task(test_UartM4255NfcModule())
    # 启动事件循环
    asyncio.get_event_loop().run_forever()
    
"""    
