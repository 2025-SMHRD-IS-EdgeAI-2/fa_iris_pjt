const express = require("express");
const router = express.Router();
const db = require("../config/db");

// 로그인 API
router.post("/login", (req, res) => {
  const { login_id, user_pwd } = req.body;

  const sql = `
    SELECT user_no, user_name
    FROM user_info
    WHERE login_id = ? AND user_pwd = ?
  `;

  db.query(sql, [login_id, user_pwd], (err, results) => {
    if (err) return res.status(500).json({ status: "error" });

    if (results.length > 0) {
      res.json({
        status: "success",
        user_no: results[0].user_no,
        user_name: results[0].user_name
      });
    } else {
      res.json({ status: "fail" });
    }
  });
});

router.post("/signup", (req, res) => {
  const { login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num } = req.body;

  const sql = `
    INSERT INTO user_info (login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `;

  db.query(sql, [login_id, user_pwd, user_name, email, gender, age, device_num, webcam_num], (err, result) => {
    if (err) {
      console.log(err);
      return res.json({ status: "fail", msg: err.message });
    }
    return res.json({
      status: "success",
      user_no: result.insertId,
      user_name: user_name
    });
   });
});

module.exports = router;
