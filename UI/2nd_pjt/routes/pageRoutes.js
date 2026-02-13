const express = require("express");
const path = require("path");


const router = express.Router();

// 첫 화면
router.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "start", "index.html"));
});

// 로그인 페이지
router.get("/login", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "login", "login.html"));
});

// 회원가입 페이지
router.get("/signup", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "signup", "signup.html"));
});

// 메인 페이지
router.get("/main", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "main", "main.html"));
});

module.exports = router;
