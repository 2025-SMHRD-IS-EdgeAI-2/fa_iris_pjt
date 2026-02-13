// ==========================================
// 1. 필요한 도구들
// ==========================================
const express = require("express");
const mysql = require("mysql2/promise");
const cors = require("cors");
const bodyParser = require("body-parser");
const path = require("path");

const app = express();
const PORT = 4000;

// ==========================================
// 2. 미들웨어 (순서 중요)
// ==========================================
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 요청 로그
app.use((req, res, next) => {
  console.log("📥 REQUEST:", req.method, req.url);
  next();
});

// 정적 파일 제공
app.use(express.static(__dirname));

// ==========================================
// 3. DB 연결
// ==========================================
const db = mysql.createPool({
  host: "project-db-cgi.smhrd.com",
  port: 3307,
  user: "2nd_pjt",
  password: "1234",
  database: "2nd_pjt",
  waitForConnections: true,
  connectionLimit: 10,
  charset: "utf8mb4",
});
// ==========================================
// 4. 학습 시작 → FastAPI 중계
// ==========================================
app.post('/start-learning', async (req, res) => {
    const { user_no } = req.body;

    try {
        const response = await fetch("http://192.168.219.177:3000", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            login_id: idVal,
            user_pwd: pwVal
          })
        });

        const data = await response.json();
        res.json(data);

    } catch (err) {
        console.error("AI 서버 연결 실패:", err);
        res.status(500).json({ status: "error" });
    }
});

// ==========================================
// 4-1. 회원가입 → FastAPI 중계
// ==========================================

app.post("/api/signup", (req, res) => {
  const { login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num } = req.body;

  const sql = `
    INSERT INTO user_info 
    (login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;

  db.query(sql, [login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num], (err) => {
    if (err) {
      console.error("회원가입 에러:", err.message);
      return res.status(500).json({ status: "error", msg: err.message });
    }
    res.json({ status: "success" });
  });
});

// ==========================================
// 4-2. 로그인 → FastAPI 중계
// ==========================================

app.post("/api/login", async (req, res) => {
  const { login_id, user_pwd } = req.body;
  console.log("🔥 로그인 요청:", req.body);

  if (!login_id || !user_pwd) {
    return res.status(400).json({ status: "fail", msg: "값 없음" });
  }

  try {
    const sql = `
      SELECT user_no, user_name, email
      FROM user_info
      WHERE login_id = ? AND user_pwd = ?
    `;

    const [rows] = await db.query(sql, [login_id, user_pwd]);

    if (rows.length === 0) {
      return res.json({
        status: "fail",
        msg: "아이디 또는 비밀번호가 틀렸습니다."
      });
    }

    res.json({
      status: "success",
      user_no: rows[0].user_no,
      name: rows[0].user_name,
      email: rows[0].email
    });

  } catch (err) {
    console.error("❌ 로그인 에러:", err);
    res.status(500).json({ status: "error" });
  }
});

// ==========================================
// 4-3. 유저 정보 불러오기 (DB 조회)
// ==========================================
    app.get("/user/:user_no", (req, res) => {
    const user_no = req.params.user_no;

    const sql = `
        SELECT user_no, user_name, email, gender, age, device_num, webcam_num
        FROM user_info
        WHERE user_no = ?
    `;

    db.query(sql, [user_no], (err, results) => {
        if (err) {
        console.error("유저 조회 에러:", err.message);
        return res.status(500).json({ status: "error", msg: err.message });
        }

        if (results.length === 0) {
        return res.json({ status: "fail", msg: "유저 없음" });
        }

        res.json({ status: "success", user: results[0] });
    });
    });

// ==========================================
// ⭐ 4-4. 집중도 / 스트레스 그래프 데이터 조회 (여기에 추가!!!)
// ==========================================

// 집중도 7일
      app.get("/api/focus/week/:user_no", (req, res) => {
        const user_no = req.params.user_no;

        const sql = `
          SELECT DATE(created_at) AS day, focus_score
          FROM study_record
          WHERE user_no = ?
          ORDER BY created_at DESC
          LIMIT 7
        `;

        db.query(sql, [user_no], (err, results) => {
          if (err) {
            console.error("집중도 조회 에러:", err.message);
            return res.status(500).json({ status: "error" });
          }

          res.json({ status: "success", data: results });
        });
      });

      // 스트레스 7일
      app.get("/api/stress/week/:user_no", (req, res) => {
        const user_no = req.params.user_no;

        const sql = `
          SELECT DATE(created_at) AS day, stress_score
          FROM study_record
          WHERE user_no = ?
          ORDER BY created_at DESC
          LIMIT 7
        `;

        db.query(sql, [user_no], (err, results) => {
          if (err) {
            console.error("스트레스 조회 에러:", err.message);
            return res.status(500).json({ status: "error" });
          }

          res.json({ status: "success", data: results });
        });
      });



// ==========================================
// 5. 서버 실행
// ==========================================

app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 서버 실행 http://192.168.219.128:${PORT}`);
});

//app.use(express.static(path.join(__dirname, "public")));



// ==========================================
// 6. 학습 시작/종료 명령 저장 (Python 클라이언트용)
// ==========================================

let commandState = {
  status: "stop",  // start / stop
  user_no: null
};

// 학습 시작 명령
app.post("/command/start", (req, res) => {
  const { user_no } = req.body;

  commandState.status = "start";
  commandState.user_no = user_no;

  console.log("✅ START 명령 발생:", commandState);
  res.json({ status: "success", commandState });
});

// 학습 종료 명령
app.post("/command/stop", (req, res) => {
  commandState.status = "stop";
  commandState.user_no = null;

  console.log("🛑 STOP 명령 발생:", commandState);
  res.json({ status: "success", commandState });
});

// Python이 명령 확인하는 API
app.get("/command", (req, res) => {
  res.json(commandState);
});

// Python이 분석 결과 업로드하는 API
app.post("/result", (req, res) => {
  console.log("📩 Python 결과 수신:", req.body);

  // 여기서 DB 저장까지 하려면 추가로 INSERT 하면 됨
  res.json({ status: "success" });
});

// ==============================
// 📊 메인 대시보드 데이터
// ==============================
app.get("/api/dashboard/:user_no", async (req, res) => {
  try {
    const user_no = req.params.user_no;

    const [userRows] = await db.query(
      "SELECT user_name FROM user_info WHERE user_no = ?",
      [user_no]
    );

    const [reportRows] = await db.query(
      `SELECT report_date, avg_focus_score, avg_stress_score
       FROM daily_reports
       WHERE user_no = ?
       ORDER BY report_date ASC`,
      [user_no]
    );

    res.json({
      status: "success",
      name: userRows[0].user_name,
      reports: reportRows
    });

  } catch (err) {
    console.error("❌ dashboard 에러:", err);
    res.status(500).json({ status: "error" });
  }
});


app.post("/api/daily_report", async (req, res) => {
  const { user_no, report_date, star_rating, content } = req.body;

  try {
    const sql = `
      INSERT INTO daily_reports (user_no, report_date, star_rating, content)
      VALUES (?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE
        star_rating = VALUES(star_rating),
        content = VALUES(content)
    `;

    await db.query(sql, [
      user_no,
      report_date,
      star_rating,
      content
    ]);

    res.json({ status: "success" });
  } catch (err) {
    console.error("❌ daily_report 저장 에러:", err);
    res.status(500).json({ status: "error" });
  }
});


// 자격증 정보 불러오기
app.post("/api/licence", async (req, res) => {
  const {
    user_no,
    licence_kind,
    licence_start,
    licence_end,
    licence_feedback
  } = req.body;

  if (!user_no || !licence_kind || !licence_start) {
    return res.status(400).json({ status: "fail", msg: "필수값 누락" });
  }

  try {
    const sql = `
      INSERT INTO licence_prep
      (user_no, licence_kind, licence_start, licence_end, licence_feedback)
      VALUES (?, ?, ?, ?, ?)
    `;

    await db.query(sql, [
      user_no,
      licence_kind,
      licence_start,
      licence_end || null,
      licence_feedback || null
    ]);

    res.json({ status: "success" });

  } catch (err) {
    console.error("❌ licence 저장 에러:", err);
    res.status(500).json({ status: "error" });
  }
});

// DATA 연동 //
app.get("/api/daily-report", async (req, res) => {
  const { user_no, date } = req.query;

  try {
    // 1️⃣ daily_reports
    const [reportRows] = await db.query(
      `
      SELECT
        avg_focus_score   AS avg_focus,
        avg_stress_score  AS avg_stress,
        feedback_comment  AS feedback,
        content           AS diary
      FROM daily_reports
      WHERE user_no = ? AND report_date = ?
      `,
      [user_no, date]
    );

    // 2️⃣ study_record — 🔥 핵심 수정
    const today = new Date();
    const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 0, 0, 0);
    const endOfDay   = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1, 0, 0, 0);

    const startStr = startOfDay.toISOString().slice(0, 19).replace('T', ' ');
    const endStr   = endOfDay.toISOString().slice(0, 19).replace('T', ' ');


    const [timeRows] = await db.query(
      `
      SELECT
        SUM(TIMESTAMPDIFF(SECOND, start_time, end_time)) AS total_seconds
      FROM study_record
      WHERE user_no = ? AND DATE(start_time) = ?
      `,
      [user_no, date]
    );

    const totalSec = timeRows[0].total_seconds; // null이면 측정 안 함
    res.json({
      status: "success",
      data: {
        ...(reportRows[0] || {}),
        total_seconds: timeRows[0].total_seconds  
      }
    });

  } catch (err) {
    console.error("❌ daily-report 조회 에러:", err);
    res.status(500).json({ status: "error" });
  }
});


// 회원 정보 조회
app.get("/api/profile", async (req, res) => {
  const userNo = 1; // 지금은 고정 (나중에 로그인 연동)

  const [rows] = await db.query(
    `SELECT user_no, login_id, user_name, email, gender, age, created_at
     FROM user_info
     WHERE user_no = ?`,
    [userNo]
  );

  res.json(rows[0]);
});

// 회원 정보 수정
app.put("/api/profile", async (req, res) => {
  const userNo = 1;

  const { user_name, email, gender, age } = req.body;

  await db.query(
    `UPDATE user_info
     SET user_name=?, email=?, gender=?, age=?
     WHERE user_no=?`,
    [user_name, email, gender, age, userNo]
  );

  res.json({ success: true });
});

// 자격 정보
app.get("/api/licence/:user_no", async (req, res) => {
  const { user_no } = req.params;

  try {
    const [rows] = await db.query(
      `
      SELECT
        licence_kind,
        licence_start,
        licence_end,
        licence_feedback
      FROM licence_prep
      WHERE user_no = ?
      ORDER BY prepare_no DESC
      LIMIT 1
      `,
      [user_no]
    );

    if (rows.length === 0) {
      return res.json({
        status: "empty",
        data: null
      });
    }

    res.json({
      status: "success",
      data: rows[0]
    });

  } catch (err) {
    console.error("❌ licence 조회 에러:", err);
    res.status(500).json({ status: "error" });
  }
});
