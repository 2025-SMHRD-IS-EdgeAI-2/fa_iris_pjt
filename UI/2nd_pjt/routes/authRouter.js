const express = require("express");
const db = require("../config/db");

const router = express.Router();

// 회원가입
router.post("/signup", (req, res) => {
  const { login_id, user_pwd, user_name, email, gender, age } = req.body;

  const sql =
    "INSERT INTO user_info (login_id, user_pwd, user_name, email, gender, age) VALUES (?, ?, ?, ?, ?, ?)";

  db.query(sql, [login_id, user_pwd, user_name, email, gender, age], (err) => {
    if (err) {
      console.error("회원가입 에러:", err.message);
      return res.status(500).json({ status: "error", msg: err.message });
    }
    res.json({ status: "success" });
  });
});

// 로그인
router.post("/login", (req, res) => {
  const { login_id, user_pwd } = req.body;

  const sql =
    "SELECT user_no, user_name FROM user_info WHERE login_id = ? AND user_pwd = ?";

  db.query(sql, [login_id, user_pwd], (err, results) => {
    if (err) {
      console.error("로그인 에러:", err.message);
      return res.status(500).json({ status: "error", msg: err.message });
    }

    if (results.length > 0) {
      res.json({
        status: "success",
        user_no: results[0].user_no,
        name: results[0].user_name,
      });
    } else {
      res.json({ status: "fail", msg: "아이디 또는 비밀번호를 확인해주세요." });
    }
  });
});

module.exports = router;
