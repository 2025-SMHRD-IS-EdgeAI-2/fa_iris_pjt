const stressEl = document.getElementById("stressScore");
const focusEl = document.getElementById("focusScore");
const feedbackEl = document.getElementById("feedbackText");
const diaryEl = document.getElementById("diaryText");
const studyTimeEl = document.getElementById("studyTime");


async function loadDailyReport(dateObj) {
  const userNo = localStorage.getItem("user_no");
  if (!userNo || !dateObj) return;

  const dateStr =
    typeof dateObj === "string"
      ? dateObj
      : `${dateObj.getFullYear()}-${String(dateObj.getMonth()+1).padStart(2,"0")}-${String(dateObj.getDate()).padStart(2,"0")}`;

  try {
    const res = await fetch(
      `http://192.168.219.128:4000/api/daily-report?user_no=${userNo}&date=${dateStr}`
    );

    const result = await res.json();
    console.log("📊 daily-report:", result);

    if (!result.data) return;

    stressEl.textContent = result.data.avg_stress ?? "-";
    focusEl.textContent = result.data.avg_focus ?? "-";
    feedbackEl.textContent = result.data.feedback || "피드백 없음";
    diaryEl.textContent = result.data.diary || "학습일지 없음";

    const totalSec = result.data.total_seconds;
    if(totalSec === null || totalSec === 0) studyTimeEl.textContent = "측정 없음";
    else {
        const hours = Math.floor(totalSec/3600);
        const minutes = Math.floor((totalSec%3600)/60);
        studyTimeEl.textContent = `${hours}시간 ${minutes}분`;
    }
  } catch (err) {
    console.error("❌ fetch 실패:", err);
  }
}

loadDailyReport();