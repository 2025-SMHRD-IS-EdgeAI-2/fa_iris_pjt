const express = require("express");
const path = require("path");
const { spawn } = require("child_process");

const router = express.Router();

// 파이썬 경로 설정
const pythonEnvPath = "C:/Users/smhrd/.conda/envs/mp_fix/python.exe";
const aiServerDir = path.join(__dirname, "..", "..", "ai_server");
const mainPyPath = path.join(aiServerDir, "main.py");

let currentPyProcess = null;

// 학습 시작
router.post("/start-learning", (req, res) => {
  const { user_no } = req.body;

  const pyProc = spawn(pythonEnvPath, [mainPyPath, user_no], {
    cwd: aiServerDir,
    env: { ...process.env, PYTHONIOENCODING: "utf-8" },
  });

  currentPyProcess = pyProc;

  let aiFeedbackText = "";

  pyProc.stdout.on("data", (data) => {
    const msg = data.toString().trim();

    if (msg.includes("AI_MSG:")) {
      const parts = msg.split("AI_MSG:");
      if (parts.length > 1) aiFeedbackText = parts[1].trim();
    }
  });

  pyProc.stderr.on("data", (data) => {
    console.error(data.toString().trim());
  });

  pyProc.on("close", () => {
    if (!aiFeedbackText) aiFeedbackText = "분석 완료 (AI 응답 없음)";
    res.json({ status: "finished", message: aiFeedbackText });
  });
});

// 학습 중단
router.post("/stop-learning", (req, res) => {
  if (currentPyProcess) {
    currentPyProcess.kill("SIGINT");
    currentPyProcess = null;
    res.json({ status: "stopped" });
  } else {
    res.status(400).json({ error: "실행 중인 학습이 없습니다." });
  }
});

module.exports = router;
