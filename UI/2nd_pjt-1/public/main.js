// ==========================================
// public/main.js
// 역할: 학습 시작 버튼 → 서버에 요청
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startBtn");

    if (!startBtn) {
        console.error("❌ startBtn 요소를 찾을 수 없음");
        return;
    }

    startBtn.addEventListener("click", async () => {
        try {
            console.log("▶ 학습 시작 버튼 클릭");

            const response = await fetch("/start-learning", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_no: 1   // 임시 테스트용
                })
            });

            const result = await response.json();
            console.log("✅ 서버 응답:", result);

            alert("학습이 시작되었습니다!");

        } catch (err) {
            console.error("❌ 학습 시작 요청 실패:", err);
            alert("서버 통신 오류");
        }
    });
});
