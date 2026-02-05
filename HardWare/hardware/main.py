import time
import statistics
from datetime import datetime
import traceback
import requests  # ★ 추가됨: 서버 통신용 라이브러리
import json      # ★ 추가됨: JSON 데이터 처리

from sensors.gsr_sensor1 import GSRSensor
from sensors.hr_sensor import HRSensor
from stress.rule_engine import calculate_stress

import lcd
import switch

import sys
import io

# UTF-8 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)

# =========================
# ★ 사용자 설정 (값 잘 들어온다고 하신 설정 반영)
MEASURE_TIME = 20       
SAMPLE_INTERVAL = 1.0   
STABLE_COUNT = 3        

# ★ [중요] 서버 주소 설정 (본인의 서버 IP로 변경 필수!)
# 예: "http://192.168.0.10:3002/api/stress" 
# 경로(/api/stress 등)는 서버 코드의 라우터 설정에 맞춰야 합니다.
SERVER_URL = "http://192.168.219.128:3002/api/study_record"
# =========================

def stress_level_text(score):
    if score <= 25:
        return "Stable"
    elif score <= 50:
        return "Mild Stress"
    elif score <= 75:
        return "Mid Stress"
    else:
        return "High Stress"

# -------------------------
# ★ 추가된 함수: 서버로 데이터 전송
def send_to_server(score, level):
    # 서버 코드의 const { stress_score } = req.body; 와 이름을 맞춰야 합니다.
    payload = {
        "stress_score": score  # ★ Key 이름을 stress_score로 변경
    }
    
    print(f"\n[전송] 서버({SERVER_URL})로 데이터 전송 시도... (Data: {payload})")
    
    try:
        # JSON 형식으로 전송
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            print("   >> 전송 성공! 서버 응답:", response.json())
            return True
        else:
            print(f"   >> 전송 실패 (Status: {response.status_code})")
            print(f"   >> 응답 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"   >> [에러] 연결 실패: {e}")
        return False

# -------------------------
def stable_read(read_func, key):
    values = []
    for _ in range(STABLE_COUNT):
        try:
            data = read_func()
            if data is None: continue
            if key not in data: continue
            values.append(data[key])
        except: pass
        time.sleep(0.1)

    if len(values) < 2: # 안정화 카운트가 3으로 줄었으므로 최소 2개면 통과
        return None
    return sum(values) / len(values)

# -------------------------
def measure_stress(gsr, hr):
    print("\n[측정] 스트레스 측정 시작")
    lcd.write(1, "Measuring...")
    lcd.write(2, "Please wait")

    stress_values = []
    start = time.time()

    while time.time() - start < MEASURE_TIME:
        gsr_v = stable_read(gsr.read, "gsr") 
        hr_bpm = stable_read(hr.read, "hr")
        
        # 값이 없으면 대기 후 다시 시도
        if gsr_v is None or hr_bpm is None:
            print(f"⏱ {int(time.time()-start):02d}s | 센서 값 대기중...")
            time.sleep(1)
            continue
        
        # 값 출력
        print(f"⏱ {int(time.time()-start):02d}s | GSR={gsr_v:.3f}V | HR={hr_bpm:.1f}")

        try:
            stress = calculate_stress({"voltage": gsr_v}, {"bpm": hr_bpm})
        except:
            stress = 50

        stress_values.append(stress)
        time.sleep(SAMPLE_INTERVAL)

    if len(stress_values) < 3: # 데이터 개수 기준 완화
        print("유효한 측정값 부족")
        return None

    cut = int(len(stress_values) * 0.3)
    # 데이터가 너무 적으면 전체 평균, 많으면 앞부분 자르기
    if cut > 0:
        final = int(statistics.median(stress_values[cut:]))
    else:
        final = int(statistics.median(stress_values))

    return final

# =========================
if __name__ == "__main__":
    try:
        print("==== 시스템 시작 ====")
        lcd.init()
        lcd.clear()
        
        gsr = GSRSensor()
        print("[초기화] GSR 캘리브레이션")
        baseline = gsr.calibrate(duration=3) # 시간 단축

        print("[초기화] HR 센서")
        hr = HRSensor()
        hr.setup()
        
        # 시작 전 LCD 표시
        lcd.write(1, "System Ready")
        lcd.write(2, "Switch ON")

        state = "IDLE"

        while True:
            if state == "IDLE":
                if switch.is_on():
                    state = "MEASURE"
                    time.sleep(0.5)

            elif state == "MEASURE":
                result = measure_stress(gsr, hr)
                
                if result is None:
                    print("측정 실패")
                    lcd.clear()
                    lcd.write(1, "Measure Fail")
                    lcd.write(2, "Try Again")
                else:
                    level_text = stress_level_text(result)
                    print("\n===== 측정 완료 =====")
                    print(f"Stress Index : {result}")
                    print(f"Level        : {level_text}")

                    lcd.clear()
                    lcd.write(1, f"Stress: {result}")
                    lcd.write(2, level_text)
                    
                    # ★ 여기서 서버로 전송
                    lcd.write(2, "Sending...") # LCD에 전송중 표시
                    send_to_server(result, level_text)
                    
                    # 전송 후 다시 결과 표시
                    lcd.write(2, level_text) 

                time.sleep(3) 
                state = "WAIT"

            elif state == "WAIT":
                if not switch.is_on():
                    lcd.clear()
                    lcd.write(1, "System Ready")
                    lcd.write(2, "Switch ON")
                    state = "IDLE"
            
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n시스템 종료")
        lcd.clear()
        switch.cleanup()