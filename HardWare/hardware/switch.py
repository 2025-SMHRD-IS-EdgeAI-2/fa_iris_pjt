import RPi.GPIO as GPIO

SWITCH_PIN = 27  # BCM 기준

# ===== GPIO 초기화 =====
GPIO.setmode(GPIO.BCM)          # ★ 이 줄이 빠져서 터진 거다
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def is_on():
    # ON/OFF 스위치: ON일 때 GND 연결 → LOW
    return GPIO.input(SWITCH_PIN) == GPIO.LOW

def cleanup():
    GPIO.cleanup(SWITCH_PIN)