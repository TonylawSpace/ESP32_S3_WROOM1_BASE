# main.py
# -*- coding: utf-8 -*-
import uasyncio as asyncio

import network
import machine
import time
import gc
import os 
import ubinascii

from multi_task_system import MultiTaskSystem

# 在文件开头定义 DEBUG 常量 根據環境設置參數的值的大小
DEBUG = True  # 调试时设为 True，发布时设为 False 
 
# 启动系统
if __name__ == "__main__":
    system = MultiTaskSystem()
    system.run()
    
    
    
