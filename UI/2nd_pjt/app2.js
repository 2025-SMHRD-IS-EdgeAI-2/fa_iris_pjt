// ==========================================
// 1. 필요한 도구들
// ==========================================
const express = require("express");
const mysql = require("mysql2");
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
// 4-1. 회원가입
// ==========================================
app.post("/api/signup", (req, res) => {
  const {
    login_id,
    user_pwd,
    user_name,
    email,
    gender,
    age,
    device_num,
    webcam_num,
  } = req.body;

  const sql = `
    INSERT INTO user_info
    (login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;

  db.query(
    sql,
    [login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num],
    (err) => {
      if (err) {
        console.error("회원가입 에러:", err);
        return res.status(500).json({ status: "error" });
      }
      res.json({ status: "success" });
    }
  );
});

// ==========================================
// 4-2. 로그인 (핵심)
// ==========================================
app.post("/api/login", (req, res) => {
  const { login_id, user_pwd } = req.body;

  console.log("🔥 로그인 요청:", req.body);

  if (!login_id || !user_pwd) {
    return res.status(400).json({ status: "fail", msg: "값 없음" });
  }

  const sql = `
    SELECT user_no, user_name, email
    FROM user_info
    WHERE login_id = ? AND user_pwd = ?
  `;

  db.query(sql, [login_id, user_pwd], (err, results) => {
    if (err) {
      console.error("로그인 에러:", err);
      return res.status(500).json({ status: "error" });
    }

    if (results.length === 0) {
      return res.json({
        status: "fail",
        msg: "아이디 또는 비밀번호가 틀렸습니다."
      });
    }

    res.json({
      status: "success",
      user_no: results[0].user_no,
      name: results[0].user_name,
      email: results[0].email
    });
  });
});

// ==========================================
// 5. 서버 실행
// ==========================================
app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 서버 실행 http://192.168.219.128:${PORT}`);
});