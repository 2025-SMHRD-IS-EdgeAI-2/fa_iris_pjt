const express = require('express');
const router = express.Router();
const db = require('../config/db');

//일단 테스트 사용자 고정
const TEST_LOGIN_ID = '승현';
const TEST_USER_PWD = '1234';

router.post('/study_record', (req, res) => {
    const { stress_score } = req.body;

    console.log('수신 데이터:', req.body);

    if (stress_score === undefined) {
        return res.status(400).json({ error: 'invalid data' });
    }

    // user_no 조회 (서버에서)
    const userSql = `
        SELECT user_no
        FROM user_info
        WHERE login_id = ?
          AND user_pwd = ?
    `;

    db.query(userSql, [TEST_LOGIN_ID, TEST_USER_PWD], (err, users) => {
        if (err) return res.status(500).json({ error: err.message });
        if (users.length === 0)
            return res.status(404).json({ error: 'user not found' });

        const user_no = users[0].user_no;
        const today = new Date().toISOString().slice(0, 10);

        // daily_reports 평균값 갱신
        const reportSql = `
            INSERT INTO daily_reports (user_no, report_date, avg_stress_score)
            VALUES (?, ?, ?)
            ON DUPLICATE KEY UPDATE
            avg_stress_score = ROUND(
                (avg_stress_score + VALUES(avg_stress_score)) / 2,
                2
            )
        `;

        db.query(reportSql, [user_no, today, stress_score], (err2) => {
            if (err2) return res.status(500).json({ error: err2.message });

            res.json({
                status: 'ok',
                user_no,
                stress_score
            });
        });
    });
});

module.exports = router;