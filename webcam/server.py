# ==========================================
# [파일] server.py (팀장님 환경 최적화 통합본)
# ==========================================
from fastapi import FastAPI
from pydantic import BaseModel
import pymysql
import requests
from typing import Optional
import subprocess
import sys
import uvicorn
import time

app = FastAPI()

# ==========================================
# 1. 설정 및 상수 (랑랑 & 팀장님 공통)
# ==========================================
GEMINI_API_KEY = "1"

DB_CONFIG = {
    "host": "project-db-cgi.smhrd.com",
    "port": 3307,
    "user": "2nd_pjt",
    "password": "1234",
    "db": "2nd_pjt",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
    "connect_timeout": 5  # 팀장님 코드의 안정성 설정 반영
}

# ==========================================
# 2. 데이터 모델 (DTO)
# ==========================================
class StartLearningReq(BaseModel):
    user_no: int
    licence_kind: Optional[str] = None # 팀장님 코드의 자격증 인자 반영

class RecordModel(BaseModel):
    user_no: int
    focus_score: int
    stress_score: int = 0

# ==========================================
# 3. Gemini 호출 함수 (자동 모델 스위칭 로직)
# ==========================================
def call_gemini(prompt, timeout=10):
    """
    1순위 모델이 막히면 다음 모델로 자동 전환하여 
    팀장님 PC에서도 AI 응답 누락을 최소화합니다.
    """
    if not GEMINI_API_KEY: 
        return "오늘도 고생하셨습니다."

    candidate_models = [
        "gemini-2.0-flash",       # 1순위: 최신 (가장 빠름)
        "gemini-flash-latest",    # 2순위: 안정화 버전
        "gemini-pro"              # 3순위: 구형 (가장 안정적)
    ]

    for model_name in candidate_models:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            f"?key={GEMINI_API_KEY}"
        )
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        for attempt in range(2): # 모델당 2회 재시도
            try:
                res = requests.post(url, json=data, timeout=timeout)

                if res.status_code == 200:
                    print(f"✅ [AI 성공] {model_name} 응답 완료", flush=True)
                    return res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                
                elif res.status_code in [404, 429]: # 모델 없음 혹은 과부하 시 즉시 다음 모델로
                    print(f"⚠️ [AI 전환] {model_name} 스킵 (코드: {res.status_code})", flush=True)
                    break 

                elif res.status_code == 503:
                    time.sleep(2)
                    continue
            except:
                continue
    
    return "오늘도 자격증 합격을 위해 고생 많으셨습니다! (시스템 자동 피드백)"

# ==========================================
# 4. 학습 시작 API (Node.js & main.py 연결)
# ==========================================
@app.post("/start-learning")
async def start_learning(data: StartLearningReq):
    try:
        # 팀장님 코드의 인자 전달 방식(sys.executable) 반영
        args = [sys.executable, "main.py", str(data.user_no)]
        if data.licence_kind: 
            args.append(data.licence_kind)
            
        subprocess.Popen(args)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        return {"status": "error"}

# ==========================================
# 5. 실시간 기록 저장 API
# ==========================================
@app.post("/record")
def save_record(data: RecordModel):
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = """
                INSERT INTO study_record 
                (user_no, start_time, end_time, focus_score, stress_score)
                VALUES (%s, NOW(), DATE_ADD(NOW(), INTERVAL 5 SECOND), %s, %s)
            """
            cur.execute(sql, (data.user_no, data.focus_score, data.stress_score))
        return {"msg": "saved"}
    except Exception as e:
        print(f"❌ DB 저장 실패: {e}")
        return {"msg": "db_error"}
    finally:
        if conn: conn.close()

# ==========================================
# 6. 일일 리포트 및 라이센스 피드백 API (통합본)
# ==========================================
@app.post("/report/daily")
def create_daily_report(data: RecordModel):
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            
            # [Step 1] 오늘 평균 계산 (float/round 처리로 데이터 정밀도 유지)
            sql_today = """
                SELECT AVG(focus_score) as af, AVG(stress_score) as as_
                FROM study_record
                WHERE user_no=%s AND DATE(start_time)=CURDATE()
            """
            cur.execute(sql_today, (data.user_no,))
            stats = cur.fetchone()

            af = round(float(stats['af']), 2) if stats and stats['af'] else float(data.focus_score)
            as_ = round(float(stats['as_']), 2) if stats and stats['as_'] else 0.0

            # [Step 2] 오늘의 AI 피드백
            daily_prompt = f"평균집중도 {af}, 스트레스 {as_}. 격려 50자 이내."
            daily_comment = call_gemini(daily_prompt)

            # DB 저장 (ON DUPLICATE KEY UPDATE로 팀장님 코드의 갱신 로직 반영)
            sql_save_daily = """
                INSERT INTO daily_reports 
                (user_no, report_date, avg_focus_score, avg_stress_score, feedback_comment)
                VALUES (%s, CURDATE(), %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    avg_focus_score=VALUES(avg_focus_score),
                    avg_stress_score=VALUES(avg_stress_score),
                    feedback_comment=VALUES(feedback_comment)
            """
            cur.execute(sql_save_daily, (data.user_no, af, as_, daily_comment))

            # [Step 3] 라이센스 기간별 누적 피드백 (랑랑의 핵심 로직)
            sql_lic = "SELECT prepare_no, licence_kind, licence_start, licence_end FROM licence_prep WHERE user_no=%s LIMIT 1"
            cur.execute(sql_lic, (data.user_no,))
            licence = cur.fetchone()

            if licence:
                start_date = licence['licence_start']
                end_date = licence['licence_end'] or "9999-12-31"

                sql_period_avg = "SELECT AVG(avg_focus_score) p_f, AVG(avg_stress_score) p_s FROM daily_reports WHERE user_no=%s AND report_date BETWEEN %s AND %s"
                cur.execute(sql_period_avg, (data.user_no, start_date, end_date))
                p_stats = cur.fetchone()
                
                pf = round(float(p_stats['p_f']), 2) if p_stats and p_stats['p_f'] else 0.0
                ps = round(float(p_stats['p_s']), 2) if p_stats and p_stats['p_s'] else 0.0

                l_prompt = f"자격증 {licence['licence_kind']} 준비. 누적집중도 {pf}, 스트레스 {ps}. 격려 80자 이내."
                l_feedback = call_gemini(l_prompt)

                sql_up_lic = "UPDATE licence_prep SET licence_feedback=%s WHERE prepare_no=%s"
                cur.execute(sql_up_lic, (l_feedback, licence['prepare_no']))

            conn.commit()
            print(f"✅ [리포트 완료] 유저 {data.user_no} 데이터 갱신 성공", flush=True)

        return {"msg": "success", "ai_feedback": daily_comment}

    except Exception as e:
        print(f"❌ 리포트 생성 오류: {e}")
        return {"msg": "error"}
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)