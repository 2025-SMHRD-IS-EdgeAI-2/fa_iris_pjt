const swipeArea = document.getElementById("date-swipe");
const monthText = document.getElementById("monthText");

const dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

const dayNumEls = {
  "-2": document.getElementById("dayNum-2"),
  "-1": document.getElementById("dayNum-1"),
  "0":  document.getElementById("dayNum-0"),
  "1":  document.getElementById("dayNum-1p"),
  "2":  document.getElementById("dayNum-2p"),
};

const dayNameEls = {
  "-2": document.getElementById("dayName-2"),
  "-1": document.getElementById("dayName-1"),
  "0":  document.getElementById("dayName-0"),
  "1":  document.getElementById("dayName-1p"),
  "2":  document.getElementById("dayName-2p"),
};

// ✅ 날짜 상태는 여기 하나만
const savedDate = localStorage.getItem("selected_date");
let currentDate = savedDate
  ? new Date(savedDate + "T12:00:00") // 정오 기준
  : new Date();

function renderDates() {
  for (let offset = -2; offset <= 2; offset++) {
    const d = new Date(currentDate);
    d.setDate(currentDate.getDate() + offset);

    dayNumEls[offset].textContent = d.getDate();
    dayNameEls[offset].textContent = dayNames[d.getDay()];
  }

  monthText.textContent = monthNames[currentDate.getMonth()];

  // data.js 로딩 후에만 호출
  if (typeof window.loadDailyReport === "function") {
    window.loadDailyReport(currentDate);
  }
}

renderDates();

/* swipe */
let startX = 0;

swipeArea.addEventListener("touchstart", e => {
  startX = e.touches[0].clientX;
});

swipeArea.addEventListener("touchend", e => {
  const diff = e.changedTouches[0].clientX - startX;
  if (Math.abs(diff) < 40) return;

  currentDate.setDate(
    currentDate.getDate() + (diff < 0 ? 1 : -1)
  );

  renderDates();
});

function moveDate(diff) {
  currentDate.setDate(currentDate.getDate() + diff);
  renderDates();

  // 🔥 날짜 바뀌면 데이터 다시 불러오기
  if (typeof loadDailyReport === "function") {
    loadDailyReport(currentDate);
  }
}