# -*- coding: utf-8 -*-
import uasyncio as asyncio
from machine import UART, Pin
import time
import binascii
import LCD1602

print("拍卡器监听模组已启动...\nThe card reader monitoring module has been activated...\n")
print("请将卡片靠近读卡器\nPut the card close to the reader\n")

lcd_lock = asyncio.Lock()

class UartM4255NfcModule:
    def __init__(self, uart,lcd):
        
        print(f"UartM4255NfcModule initialized with arguments: {uart}")
        
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
            print(f"Error: insufficient data length (needed at least {end_pos} bytes, actual {len(raw_data)} bytes)")
            return None
        
        try:
            # 显示原始HEX数据
            hex_str = binascii.hexlify(raw_data).decode("utf-8").upper()
            print(f"Raw HEX Data: {hex_str}")
            
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
    def display_card_number(self, card_number):
        try:
            with self.lcd_lock:
                print("\n-------------------------------------------")
                print(f"func::display_card_number: {card_number}")
                print("-------------------------------------------\n")
                
                # 显示卡号
                self.lcd.setCursor(0, 1)
                self.lcd.printout(" " * 16)  # 清空第二行
                self.lcd.setCursor(0, 1)
                self.lcd.printout(f"Card:{card_number}")
                
                # 创建异步任务来延时清屏
                async def delayed_clear():
                    await asyncio.sleep(3)  # 等待3秒
                    self.lcd.setCursor(0, 1)
                    self.lcd.printout(" " * 16)  # 清空第二行
                
                # 直接创建任务（MicroPython的uasyncio不需要检查循环状态）
                # asyncio.create_task(delayed_clear()) # 無效
                # 改為
                time.sleep(3)   # 3 秒後 清空卡號保護隱私
                self.lcd.setCursor(0, 1)
                self.lcd.printout(" " * 16)  # 清空第二行
                
                    
        except KeyboardInterrupt:
            self.lcd.clear()
        except Exception as e:
            print(f"Error in display_card_number: {e}")
                       
            
    def uart_card_listen_and_return(self):
        """
            监听UART并返回检测到的卡号
            Monitor UART and return detected card number
        """
        last_card_id = None
        last_detect_time = 0
        
        try:
            while True:
                # 检查是否有可用数据
                # Check if data is available
                if self.uart.any():
                    bytes_available = self.uart.any()
                    print(f"\n{bytes_available} Bytes Available")
                    
                    # 读取所有可用数据
                    # Read all available data
                    data = self.uart.read()
                    
                    if data:
                        print("原始数据/Raw data:", data)
                        
                        # 解析卡号 - 使用self.uart_to_card_number
                        # Parse the card number - using self.uart_to_card_number
                        card_id = self.uart_to_card_number(data)
                        
                        if card_id is not None:
                            # 防重复读取机制
                            # Anti-duplicate read mechanism
                            current_time = time.ticks_ms()
                            if card_id != last_card_id or time.ticks_diff(current_time, last_detect_time) > 2000:
                                print(f"检测到卡号/Card number detected: {card_id}")
                                last_card_id = card_id
                                last_detect_time = current_time
                                
                                # 显示card number
                                self.display_card_number(card_id)
                                
                                # 在此添加业务逻辑（如存储卡号、控制继电器等）
                                # Add business logic here (such as storage card number, control relay, etc.)
                                print("\n")
                                print("-----------------------------------------------------------------------------------------------------")
                                print(f"在此添加业务逻辑（如存储卡号、控制继电器等）: {card_id}")
                                print(f"Add business logic here (such as storage card number, control relay, etc.): {card_id}")
                                print("-----------------------------------------------------------------------------------------------------")
                                print("\n")
                        
                        # 短暂延时防止重复读取
                        # Short delay to prevent duplicate reads
                        time.sleep(0.5)
                
                # 短暂延时减少CPU负载
                # Short delays reduce CPU load
                time.sleep_ms(300)
        
        except KeyboardInterrupt:
            print("[异常] 函数::uart_card_listen_and_return 已终止!!!")
            print("[Exception] Function::uart_card_listen_and_return has terminated!!!")
            return None

# 启动系统
if __name__ == "__main__":
    # 配置UART1：RX=GPIO18（蓝色线）对应M4255-NFC硬件针口TX
    # TX=GPIO17（紫色线）对应M4255-NFC硬件针口RX
    uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=Pin(18), tx=Pin(17))
    lcd1 = LCD1602.LCD1602(16, 2)
    uartM4255NfcModule = UartM4255NfcModule(uart1,lcd1) 
    uartM4255NfcModule.uart_card_listen_and_return()