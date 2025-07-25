from machine import UART, Pin
import time

# 配置 UART
uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=18, tx=17)
print("UART 已初始化，波特率: 9600")

print("UART 测试开始...")

while True:
    try:
        if uart.any() > 0:
            print("Received........")
            line = uart.readline()
            if line:
                print("Text line:", line.decode().strip())
        else:
            print("未检测到数据，等待中...")
        time.sleep(1)
    except Exception as e:
        print(f"发生错误: {e}")