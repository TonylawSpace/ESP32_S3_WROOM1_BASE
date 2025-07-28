import uasyncio as asyncio
import network
import ubinascii
import usocket as socket
import ujson as json
import machine
import gc
import time

# 在文件开头定义 DEBUG 常量 根據環境設置參數的值的大小
DEBUG = True  # 调试时设为 True，发布时设为 False

class ConfigServer:
    def __init__(self, port=80):
        
        # 获取设备唯一ID 提供雲端登記
        self.device_id = ubinascii.hexlify(machine.unique_id()).decode()
        
        self.port = port
        self.server_socket = None
        self.ap_ip = "192.168.4.1"
        self.current_ap_status = False
        self.ap = None
        
        self.server_task = None  # 添加异步任务引用
        
    async def start_async(self):
        """异步启动AP和配置服务器"""
        # 确保在AP模式下运行
        self.ap = network.WLAN(network.AP_IF)
        if not self.ap.active():
            print("Activating AP mode...")
            self.ap.active(True)
            await asyncio.sleep(2)  # 给AP时间启动
            
            # 设置AP参数
            self.ap.config(
                essid='DataGuardEsp', 
                password='12345678',
                channel=6,
                authmode=network.AUTH_WPA_WPA2_PSK
            )
            self.ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))
            await asyncio.sleep(3)  # 异步等待AP启动
        
        # 获取AP的实际IP
        ap_ip = self.ap.ifconfig()[0]
        print(f"AP IP: {ap_ip}")
          
        # 创建服务器套接字
        try:
            addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(addr)
            self.server_socket.listen(1)
            self.server_socket.settimeout(10) # 设置10秒超时
             
            print(f"Configuration server started at {self.ap.ifconfig()[0]}:{self.port}")
            self.current_ap_status = True
        except Exception as e:
            print(f"Failed to start server: {e}")
            self.current_ap_status = False
            return
        
        print(f"Configuration server started at {ap_ip}:{self.port}")
        self.current_ap_status = True
        
        # 主服务循环
        while self.current_ap_status:
            await self.handle_connections()
            await asyncio.sleep(0.1)  # 释放控制权
    
    async def handle_connections(self):
        """处理客户端连接"""
        try:
            client, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            
            # 设置接收超时
            client.settimeout(10.0)
            
            # 接收请求头
            request = b""
            try:
                while True:
                    chunk = client.recv(512)
                    if not chunk:
                        break
                    request += chunk
                    # 检查请求头是否结束
                    if b"\r\n\r\n" in request:
                        break
            except OSError as e:
                if str(e) != "timed out":
                    raise
            
            # 解码请求
            request_str = request.decode('utf-8')
            print(f"request_str {request_str}") # 显示接收的請求
            
            # 解析请求方法
            if "POST /update_config" in request_str:
                print("Handling config update request")
                await self.handle_config_update(client, request_str)
            elif "GET / " in request_str or "GET / HTTP" in request_str:
                print("Handling root request")
                self.handle_root_request(client)
            else:
                print(f"Unknown request: {request_str.split('\r\n')[0]}")
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"
                client.send(response.encode('utf-8'))
            
            client.close()
        except OSError as e:
            if e.args[0] != 110:  # 忽略ETIMEDOUT错误
                print(f"socket::Connection error: {str(e)}")
        except Exception as e:
            print(f"Error handling connection:  {str(e)}")
    
    async def handle_config_update(self, client, request_str):
        """处理配置更新请求 - 只处理表单数据"""
        print(f"Raw request: {request_str}")
        
        try:
            # 提取Content-Length
            content_length = 0
            for line in request_str.split('\r\n'):
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':')[1].strip())
                    break
            
            # 提取请求体
            body_start = request_str.find('\r\n\r\n') + 4
            body = request_str[body_start:body_start+content_length]
            
            # 如果需要读取更多数据
            if len(body) < content_length:
                remaining = content_length - len(body)
                body += client.recv(remaining).decode('utf-8')
            
            # 解析表单数据 (ssid=xxx&password=yyy)
            print("Parsing form data")
            config = {}
            for pair in body.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    config[key] = self.urldecode(value)
            
            print("Parsed form config:", config)
            
            # 验证配置 url_scheme and url_host 
            if 'ssid' in config and 'password' in config and 'url_scheme' in config and 'url_host' in config:
                # 保存到文件
                with open("wifi_config.json", "w") as f:
                    json.dump({"ssid": config['ssid'], "password": config['password'], "url_scheme": config['url_scheme'], "url_host": config['url_host']}, f)
                
                # 成功响应
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: text/html; charset=utf-8\r\n" 
                response += "Connection: close\r\n\r\n"
                response += self.response_config_html_message()
                
                # 确保完整发送响应
                try:
                    client.send(response.encode('utf-8')) 
                except:
                    pass
                
               
                print("Configuration saved, rebooting...")
                await asyncio.sleep(2)  # 确保数据发送完成 等待响应发送完成
                
                # 配置成功後重啟機器
                machine.reset()
            else:
                raise ValueError("Missing ssid or password in form data")
        
        except Exception as e:
            print(f"Configuration error: {e}")
            response = "HTTP/1.1 400 Bad Request\r\n"
            response += "Content-Type: text/plain; charset=utf-8\r\n"
            response += "Connection: close\r\n\r\n"
            response += f"Error: {str(e)}"
            try:
                client.send(response.encode('utf-8'))
            except:
                pass
                
    def get_current_ap_status(self):
        """獲取當前AP啟動狀態"""
        return self.current_ap_status
    
    def urldecode(self, s):
        """简单的 URL 解码函数"""
        # 替换 + 为空格
        s = s.replace('+', ' ')
        # 处理 % 编码
        parts = []
        i = 0
        while i < len(s):
            if s[i] == '%' and i+2 < len(s):
                try:
                    hex_val = s[i+1:i+3]
                    parts.append(chr(int(hex_val, 16)))
                    i += 3
                    continue
                except:
                    pass
            parts.append(s[i])
            i += 1
        return ''.join(parts)
    
    def handle_root_request(self, client):
        """处理根路径请求"""
        # 返回简单的HTML表单
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html; charset=utf-8\r\n"
        response += "Connection: close\r\n\r\n"
        response += self.get_html_form()
        try:
            client.send(response.encode('utf-8'))
        except:
            pass
    
    def get_html_form(self):
        """生成配置表单HTML（精简版）"""
        # 简化HTML以减少内存使用
        return """<!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>WiFi Config</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 20px; }
                            .container { max-width: 400px; margin: 0 auto; }
                            .form-group { margin-bottom: 15px; }
                            label { display: block; margin-bottom: 5px; }
                            input { width: 100%;  padding: 8px;max-width: 280px; }
                            button { padding: 10px; width: 100%; background: #4CAF50; color: white; border: none; }
                            .message { margin-top: 10px; padding: 10px; display: none; }
                            .success { background: #dff0d8; color: #3c763d; }
                            .error { background: #f2dede; color: #a94442; }
                            .device_id_cls{ font-size:14px;color:#3423eb; margin-top: 10px; padding: 10px; display: block; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h2>WiFi Configuration</h2>
                            <form action="/update_config" method="post" enctype="application/x-www-form-urlencoded">
                                <div class="form-group">
                                    <label for="ssid">WiFi Name (SSID)</label>
                                    <input type="text" id="ssid" name="ssid" required>
                                </div>
                                <div class="form-group">
                                    <label for="password">Password</label>
                                    <input type="text" id="password" name="password" required>
                                </div> 
                                <div class="form-group">
                                    <label for="url_scheme">Url Scheme</label>
                                    <select class="form-group" name="url_scheme" id="scheme">
                                      <option value="http">HTTP</option>
                                      <option value="https">HTTPS</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="url_host">Url Host Ip</label>
                                    <input type="text" id="url_host" name="url_host" required>
                                </div>
                                <button type="submit">Save & Reboot</button>
                            </form>
                            <div class="message" id="message"></div>
                            <div class="device_id_cls" id="device_id"><span style="color:red;font-size:14px;font-weight:600;">Device SerialNo.: </span>""" + self.device_id + """</div>
                            
                        </div> 
                    </body>
                    </html>"""
    
    
    def response_config_html_message(self):
        """生成配置表单HTML（精简版）"""
        # 简化HTML以减少内存使用
        return """<!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>ESP32 WiFi Config</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 20px; }
                            .container { max-width: 400px; margin: 0 auto; } 
                            label { display: block; margin-bottom: 5px; }
                             
                            .return_msg { margin-top: 50px; padding: 20px;  font-size:30px;}
                            .success { background: #dff0d8; color: #3c763d; }
                            .error { background: #f2dede; color: #a94442; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h2>WiFi Configuration</h2>
                              
                            <div class="return_msg" id="return_msg">
                                Configuration Successfully! <br> <br>Device will reboot. <br><br>
                                <span stye="font-size:18px;">Please reconnect to your WiFi.</span></div>
                        </div> 
                    </body>
                    </html>"""
     
    def stop(self):
        """停止服务器"""
        self.current_ap_status = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        if self.ap and self.ap.active():
            print("Disabling AP mode...")
            self.ap.active(False)
        
        print("Configuration server stopped")