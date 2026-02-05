const express = require('express');
const app = express();

const stressRouter = require('./routes/stress');

app.use(express.json());

// 테스트용
app.get('/', (req, res) => {
    res.send('Server alive');
});

// API
app.use('/api', stressRouter);

// 서버 실행
app.listen(3002, () => {
    console.log('Server running on http://localhost:3002');
});