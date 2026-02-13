# ==========================================
# 🧱 1. 라이브러리 (필요한 도구들)
# ==========================================
import sys              # 시스템 관련 도구
import io               # 한글 깨짐 방지
import time             # 시간 측정
import requests         # ⭐ 핵심: 서버 배달원
import cv2              # OpenCV
import mediapipe as mp  # 구글 AI 얼굴 분석
from collections import deque # 데이터 저장용 통
import signal           # 강제 종료 감지

# -----------------------------------------------------------
# [가독성 1순위] 한글 출력 깨짐 방지 설정
# -----------------------------------------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==========================================
# ⚙️ 2. 환경 설정 (우리 프로젝트의 약속)
# ==========================================
WINDOW_SECONDS = 60           # 30초 데이터 모음
VIDEO_PATH = 0                # 0번 웹캠
SERVER_URL = "http://127.0.0.1:8000"

# ==========================================
# 🛑 종료 신호 처리
# ==========================================
def signal_handler(sig, frame):
    print("\n🛑 종료 신호 감지! 종료합니다.", flush=True)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ==========================================
# 🎥 웹캠 열기 함수 (여러 방법 시도)
# ==========================================
def open_camera(camera_index=0):
    """
    여러 백엔드를 순차적으로 시도하여 웹캠을 엽니다.
    Windows에서 DSHOW, MSMF, 기본 백엔드 순으로 시도합니다.
    """
    backends = [
        (cv2.CAP_MSMF, "MSMF (Windows Media Foundation)"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_ANY, "기본 백엔드"),
    ]
    
    for backend, name in backends:
        print(f"🔍 {name} 시도 중...", flush=True)
        cap = cv2.VideoCapture(camera_index, backend)
        
        if cap.isOpened():
            # 실제로 읽을 수 있는지 확인
            ret, frame = cap.read()
            if ret:
                print(f"✅ {name}로 카메라 열기 성공!", flush=True)
                return cap
            else:
                cap.release()
                print(f"⚠️ {name}로 열렸으나 프레임을 읽을 수 없음", flush=True)
        else:
            print(f"❌ {name} 실패", flush=True)
    
    # 모든 시도 실패
    print("\n" + "="*50, flush=True)
    print("❌ 모든 백엔드에서 카메라를 열 수 없습니다.", flush=True)
    print("\n해결 방법:", flush=True)
    print("1. 다른 프로그램이 웹캠을 사용 중인지 확인하세요", flush=True)
    print("2. Windows 설정 → 개인정보 → 카메라 권한 확인", flush=True)
    print("3. 장치 관리자에서 카메라 드라이버 확인", flush=True)
    print("4. 다른 카메라가 있다면: python main.py [회원번호] [자격증] [카메라번호]", flush=True)
    print("   예: python main.py 1 정보처리기사 1", flush=True)
    print("="*50, flush=True)
    return None

# ==========================================
# 👤 회원 번호 및 자격증 종류 가져오기
# ==========================================
def get_args():
    """
    Node.js에서 보낸 인자를 받습니다.
    순서: python main.py [회원번호] [자격증이름(선택)] [카메라번호(선택)]
    """
    user_no = 1
    license_kind = None
    camera_index = 0  # 기본 카메라

    # 1. 회원 번호 받기
    if len(sys.argv) > 1:
        try:
            user_no = int(sys.argv[1])
        except ValueError:
            print(f"⚠️ 잘못된 회원번호: {sys.argv[1]}, 기본값 1 사용", flush=True)
    
    # 2. 자격증 종류 받기
    if len(sys.argv) > 2:
        if sys.argv[2] and sys.argv[2] != "undefined" and sys.argv[2] != "null": 
            license_kind = sys.argv[2]
    
    # 3. [NEW] 카메라 번호 받기
    if len(sys.argv) > 3:
        try:
            camera_index = int(sys.argv[3])
            print(f"🎥 카메라 {camera_index}번 사용 예정", flush=True)
        except ValueError:
            print(f"⚠️ 잘못된 카메라번호: {sys.argv[3]}, 기본값 0 사용", flush=True)

    return user_no, license_kind, camera_index

# ==========================================
# 🌐 서버 전송 함수 (Fetch 방식)
# ==========================================
def save_process_log(user_no, focus_score, stress_score, duration):
    try:
        payload = {
            "user_no": user_no,
            "focus_score": focus_score,
            "stress_score": 40
        }
        requests.post(f"{SERVER_URL}/record", json=payload, timeout=10)
    except Exception as e:
        print(f"❌ 기록 전송 실패: {e}", flush=True)

# ==========================================
# 🎥 3. 메인 분석 로직
# ==========================================
def main():
    # 인자값 받아오기 (카메라 번호 포함)
    user_no, license_kind, camera_index = get_args()
    
    print(f"\n{'='*50}", flush=True)
    print(f"▶ 회원 {user_no}번 분석 시작", flush=True)
    if license_kind:
        print(f"📄 [모드 ON] 자격증: {license_kind}", flush=True)
    print(f"{'='*50}\n", flush=True)

    # ========================================
    # [핵심 수정] 여러 방법으로 카메라 열기 시도
    # ========================================
    cap = open_camera(camera_index)
    
    if cap is None:
        print("\n프로그램을 종료합니다.", flush=True)
        return

    # 카메라 설정 최적화
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📹 카메라 설정: {int(actual_width)}x{int(actual_height)} @ {int(actual_fps)}fps", flush=True)

    # MediaPipe 설정
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles

    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    focus_buffer = deque(maxlen=WINDOW_SECONDS)
    all_scores_for_report = []
    last_save_time = time.time()
    
    print("\n✅ 분석 시작! (종료하려면 'q'를 누르세요)\n", flush=True)

    try:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("⚠️ 프레임을 읽을 수 없습니다. 재시도 중...", flush=True)
                time.sleep(0.1)
                continue

            frame_count += 1
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(frame_rgb)

            focus_score = 0
            state = "No Face"

            faces = result.multi_face_landmarks

            if not faces:
                state = "No Face"
                focus_score = 0
            else:
                face_landmarks = faces[0]
                lm = face_landmarks.landmark
                
                # 눈 깜빡임 로직
                eye_diff = abs(lm[33].y - lm[263].y)

                if eye_diff < 0.005:
                    focus_score, state = 90, "Focused"
                elif eye_diff < 0.015:
                    focus_score, state = 70, "Normal"
                else:
                    focus_score, state = 40, "Distracted"

                # 화면 그리기
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    None,
                    mp_styles.get_default_face_mesh_tesselation_style()
                )

                # 1초마다 버퍼에 저장
                now = time.time()
                if now - last_save_time >= 1:
                    focus_buffer.append(focus_score)
                    last_save_time = now

                # 분당 data 전송
                if len(focus_buffer) == 60:   # WINDOW_SECONDS = 60
                    avg_focus = int(sum(focus_buffer) / len(focus_buffer))
                    save_process_log(user_no, avg_focus, 0, len(focus_buffer))
                    all_scores_for_report.append(avg_focus)
                    print(f"📊 1분 평균 집중도: {avg_focus}점", flush=True)
                    focus_buffer.clear()

            # 화면 텍스트 출력
            text = f"{state} ({focus_score})"
            if state == "No Face": 
                text = state
            
            # 상태 표시
            cv2.putText(frame, text, (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 버퍼 상태 표시
            buffer_text = f"Buffer: {len(focus_buffer)}/{WINDOW_SECONDS}s"
            cv2.putText(frame, buffer_text, (30, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # 프레임 카운트 표시
            frame_text = f"Frame: {frame_count}"
            cv2.putText(frame, frame_text, (30, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow("FA-IRIS Analysis", frame)

            # 'q' 키로 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n사용자가 종료를 요청했습니다.", flush=True)
                break

    except KeyboardInterrupt:
        print("\n\n⚠️ 키보드 인터럽트 감지!", flush=True)
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        # 자원 해제
        print("\n자원 정리 중...", flush=True)
        cap.release()
        cv2.destroyAllWindows()

        # 남은 데이터 전송
        if focus_buffer:
            avg = int(sum(focus_buffer) / len(focus_buffer))
            save_process_log(user_no, avg, 0, len(focus_buffer))
            all_scores_for_report.append(avg)
            print(f"📊 마지막 {len(focus_buffer)}초 평균: {avg}점", flush=True)

        # 전체 평균 계산
        final_avg = 0
        if all_scores_for_report:
            final_avg = int(sum(all_scores_for_report) / len(all_scores_for_report))

        print(f"\n{'='*50}", flush=True)
        print(f"📈 최종 평균 집중도: {final_avg}점", flush=True)
        print(f"📊 총 {len(all_scores_for_report)}개 구간 분석 완료", flush=True)
        print(f"{'='*50}\n", flush=True)

        final_ai_message = None



        # ==========================================
        # 1. 일일 리포트 생성 요청 (우선순위 2등)
        # ==========================================
        print(f"📝 일일 리포트 생성 중...", flush=True)
        try:
            res = requests.post(
                f"{SERVER_URL}/report/daily",
                json={"user_no": user_no, "focus_score": final_avg},
                timeout=60
            )
            if res.status_code == 200:
                print(f"✅ 리포트 생성 완료", flush=True)
                if not final_ai_message:
                    daily_msg = res.json().get("ai_feedback", "")
                    if daily_msg:
                        final_ai_message = daily_msg
            else:
                print(f"⚠️ 리포트 응답 오류: {res.status_code}", flush=True)
                
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}", flush=True)

        # ==========================================
        # [최종] Node.js에게 배달할 메시지 출력
        # ==========================================
        print(f"\n{'='*50}", flush=True)
        if final_ai_message:
            print(f"AI_MSG: {final_ai_message}", flush=True)
        else:
            print("AI_MSG: 고생하셨습니다. (데이터 분석 완료)", flush=True)
        print(f"{'='*50}\n", flush=True)

if __name__ == "__main__":
    main()







