# 雲端業務  Attendance Post API
# cloud_module.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio
from machine import Pin
from time import sleep
import urequests as requests
import time
import utime
import machine
import ntptime

# 常量與配置文件相關 Consts related to configuration files
from const_and_config import (
    device_id, DEBUG, ssid, password, 
    url_scheme, url_host, url_port, 
    api_post_path, tapping_card_led_pin, 
    winfi_led_pin
)

class CloudModule:
    def __init__(self):
        self.device_id = device_id
        self.post_validate_api = f"{url_scheme}://{url_host}:{url_port}/{api_post_path}"
        #print(f"\nPOST URL: {self.post_validate_api}\n")

    async def post_validate(self, nfc_card_number) -> bool:
        """
            异步Post 有效驗證卡號是否有效通過
            Asynchronous Post to verify whether the card number is valid
        """
        try: 
            # 构建请求数据
            post_json = {
                "deviceSerialNo": self.device_id,
                "occurDateTime": CloudModule.get_unix_time_ms(),  
                "nfcCardNumber": nfc_card_number
            }

            if DEBUG:
                print(f"POST DATA: {post_json}")
                print(f"REQUEST URL: {self.post_validate_api}")

            # 发送POST请求 - 使用异步包装器
            response = await self.async_request(
                "POST", 
                self.post_validate_api,
                json=post_json,
                headers={'Content-Type': 'application/json'}
            )

            # 解析响应
            response_data = response.json()
            response.close()  # 关闭连接

            if DEBUG:
                print(f"RESPONSE DATA: {response_data}")

            # 检查响应状态
            if response_data.get('meta', {}).get('success', True):
                return True
            else:
                if DEBUG:
                    print(f"VARIFIED FAIL: {response_data.get('meta', {}).get('message', 'UNKOWN ERROR')}")
                return False

        except KeyboardInterrupt:
            print("Program operation is interrupted")
            return False
        except Exception as e:
            if DEBUG:
                print(f"Request error: {str(e)}")
            return False

    async def async_request(self, method, url, **kwargs):
        """异步HTTP请求包装器 Asynchronous HTTP request wrapper"""
        # loop = asyncio.get_event_loop()
        # 使用小延迟释放控制权
        while True:
            await asyncio.sleep(0)
            try:
                # 同步HTTP请求
                if method == "GET":
                    return requests.get(url, **kwargs)
                elif method == "POST":
                    return requests.post(url, **kwargs)
                else:
                    raise ValueError("Unsupported HTTP method")
            except OSError as e:
                if "ENOMEM" in str(e):  # 内存不足错误
                    await asyncio.sleep(1)  # 等待1秒后重试
                    continue
                raise
             
    @staticmethod 
    def get_unix_time_ms():
         
        """返回UTC+8时区的标准Unix时间戳（毫秒），兼容MicroPython epoch"""
        # 1 获取当前时间戳（秒数，从2000-01-01开始）
        micropython_epoch_time = time.time()  # 使用time.time()获取数值时间戳
        
        # 2 转换为标准Unix epoch（1970-01-01起点）
        unix_epoch_time = micropython_epoch_time + 946684800  # 2000->1970的秒数差 
        print(f"unix_epoch_time = {unix_epoch_time}")
        
        # 3 转换为UTC+8时区（+8小时 = 28800秒）
        cst_epoch_time = unix_epoch_time + 28800
        print(f"cst_epoch_time = {cst_epoch_time} (utc)")
        
        # 4 转换为毫秒
        return int(cst_epoch_time * 1000)
     
 
        
    @staticmethod
    def test_url_connection(url):
        try:
            response = requests.get(url)
            print(f"请求成功，响应状态码 Request successful, response status code: {response.status_code}")
            response.close()
            return True
        except Exception as e:
            print(f"请求失败，错误信息 Request failed, error message: {e}")
            return False
 

"""
# 测试代码
async def main():
    cloud = CloudModule()
    card_id = "22831992583"
    result = await cloud.post_validate(card_id)
    print(f"验证结果: {result}")

# 运行测试
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("程序已终止")
"""