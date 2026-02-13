import time
import json
import os
import statistics
import requests
from datetime import date

from sensors.gsr_sensor1 import GSRSensor
from sensors.hr_sensor import HRSensor
from stress.rule_engine1 import calculate_stress

import lcd
import switch
from button import Button

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)

MEASURE_TIME = 20
BASELINE_FILE = "baseline.json"
SERVER_URL = "http://192.168.219.128:3002/api/study_record"

reset_baseline = False


def stress_text(score):
    if score <= 20: return "Very Calm"
    if score <= 40: return "Stable"
    if score <= 60: return "Mild"
    if score <= 80: return "Stress"
    return "High"


def send_to_server(score):
    try:
        requests.post(SERVER_URL, json={"stress_score": score}, timeout=3)
        print("[SERVER] sent:", score)
    except Exception as e:
        print("[SERVER] fail:", e)


def load_hr_baseline():
    if not os.path.exists(BASELINE_FILE):
        return None
    with open(BASELINE_FILE, "r") as f:
        data = json.load(f)
    if data["date"] != str(date.today()):
        return None
    return data["hr"]


def save_hr_baseline(hr_base):
    with open(BASELINE_FILE, "w") as f:
        json.dump({
            "date": str(date.today()),
            "hr": hr_base
        }, f)


def measure_hr_baseline(hr, duration=10):
    values = []
    start = time.time()
    while time.time() - start < duration:
        d = hr.read()
        if d and "hr" in d:
            values.append(d["hr"])
        time.sleep(0.5)
    return statistics.mean(values) if len(values) >= 5 else None


def measure_stress(gsr, hr, hr_base, btn):
    global reset_baseline

    if gsr.baseline is None:
        raise RuntimeError("GSR baseline is None")

    scores = []

    for sec in range(MEASURE_TIME, 0, -1):

        if btn.is_pressed():
            reset_baseline = True
            return None

        lcd.clear()
        lcd.write(1, "Measuring")
        lcd.write(2, f"{sec}s left")

        g = gsr.read()
        h = hr.read()

        if not g or not h:
            time.sleep(1)
            print("센서 불안정 (GSR 또는 HR)")
            continue

        score = calculate_stress(
            gsr_now=g["gsr"],
            gsr_base=gsr.baseline,
            hr_now=h["hr"],
            hr_base=hr_base,
            spo2_now=h.get("spo2", None)
        )

        scores.append(score)

        hr_delta = int(round(h['hr'] - hr_base))
        hr_ratio = hr_delta / hr_base
        spo2 = h.get("spo2", None)

        print(
            f"{sec}s | "
            f"GSR={g['gsr']:.4f} (Δ={g['delta']:+.4f}) | "
            f"HR={h['hr']} (Δ={hr_delta:+d}, {hr_ratio*100:+.1f}%) | "
            f"SpO2={spo2 if spo2 else 'NA'} | "
            f"SCORE={score}"
        )

        time.sleep(1)

    if len(scores) < 5:
        return 25

    return int(round(statistics.median(scores) / 5) * 5)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    lcd.init()
    lcd.clear()

    gsr = GSRSensor()
    hr = HRSensor()
    hr.setup()

    btn = Button(17)

    lcd.write(1, "System Ready")
    lcd.write(2, "Switch ON")

    while True:

        if btn.is_pressed():
            reset_baseline = True
            lcd.clear()
            lcd.write(1, "Reset Baseline")
            lcd.write(2, "Please Wait")
            time.sleep(2)

        if not switch.is_on():
            time.sleep(0.2)
            continue

        if reset_baseline:
            if os.path.exists(BASELINE_FILE):
                os.remove(BASELINE_FILE)
            reset_baseline = False

        # ---------- GSR BASELINE ----------
        lcd.clear()
        lcd.write(1, "GSR Calibrate")
        lcd.write(2, "Hold still")
        print("[BASELINE] GSR calibrate")
        gsr.calibrate(duration=5)

        print(f"[BASELINE] GSR = {gsr.baseline:.4f}")
        lcd.clear()
        lcd.write(1, "GSR Baseline")
        lcd.write(2, f"{gsr.baseline:.3f}")
        time.sleep(2)

        # ---------- HR BASELINE ----------
        hr_base = load_hr_baseline()
        if hr_base is None:
            lcd.clear()
            lcd.write(1, "HR Calibrate")
            lcd.write(2, "Hold still")
            print("[BASELINE] HR baseline")
            hr_base = measure_hr_baseline(hr)

            if hr_base is None:
                lcd.clear()
                lcd.write(1, "Baseline Fail")
                lcd.write(2, "Retry")
                time.sleep(2)
                continue

            save_hr_baseline(hr_base)

            print(f"[BASELINE] HR = {hr_base:.1f} bpm")
            lcd.clear()
            lcd.write(1, "HR Baseline")
            lcd.write(2, f"{hr_base:.1f} bpm")
            time.sleep(2)

        # ---------- SpO2 BASELINE ----------
        spo2_values = []
        start = time.time()

        lcd.clear()
        lcd.write(1, "SpO2 Calibrate")
        lcd.write(2, "Hold still")
        print("[BASELINE] SpO2 calibrate")

        while time.time() - start < 8:
            d = hr.read()
            if d and "spo2" in d and d["spo2"] is not None:
                spo2_values.append(d["spo2"])
            time.sleep(0.5)

        spo2_base = int(round(statistics.mean(spo2_values))) if len(spo2_values) >= 5 else 98

        print(f"[BASELINE] SpO2 = {spo2_base}%")
        lcd.clear()
        lcd.write(1, "SpO2 Baseline")
        lcd.write(2, f"{spo2_base}%")
        time.sleep(2)

        # ---------- MEASURE ----------
        result = measure_stress(gsr, hr, hr_base, btn)

        if reset_baseline:
            lcd.clear()
            lcd.write(1, "Baseline Reset")
            lcd.write(2, "Restarting")
            time.sleep(2)
            continue

        if result is None:
            lcd.clear()
            lcd.write(1, "Measure Fail")
            lcd.write(2, "Retry")
            time.sleep(3)
        else:
            lcd.clear()
            lcd.write(1, f"Stress {result}")
            lcd.write(2, stress_text(result))
            send_to_server(result)
            time.sleep(5)

        lcd.clear()
        lcd.write(1, "System Ready")
        lcd.write(2, "Switch OFF")

        while switch.is_on():
            time.sleep(0.2)