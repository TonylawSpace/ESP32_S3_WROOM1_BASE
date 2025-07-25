# 通过开关启动AP热点服务
from machine import Pin
import time

led = machine.Pin(18, machine.Pin.OUT)
onboard = machine.Pin(25, machine.Pin.OUT)
button = Pin(19, Pin.IN, Pin.PULL_DOWN)

led.off()
onboard.off()

while True:
    
         if(button.value()):
             onboard.on()
             led.off()
         else:
             onboard.off()
             led.on()