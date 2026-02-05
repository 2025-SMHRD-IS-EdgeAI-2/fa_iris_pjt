import time
from smbus2 import SMBus

I2C_ADDR = 0x27   # 대부분 1602 I2C 주소
bus = SMBus(1)

LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

ENABLE = 0b00000100
BACKLIGHT = 0b00001000

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits | ENABLE)
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)
    time.sleep(0.0005)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | BACKLIGHT

    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.005)

def clear():
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.002)

def write(line, text):
    if line == 1:
        lcd_byte(LCD_LINE_1, LCD_CMD)
    elif line == 2:
        lcd_byte(LCD_LINE_2, LCD_CMD)

    text = text.ljust(16)[:16]
    for char in text:
        lcd_byte(ord(char), LCD_CHR)

def cleanup():
    clear()