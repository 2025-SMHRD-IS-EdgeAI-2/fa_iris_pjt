const mysql = require('mysql2');

const db = mysql.createPool({
    host: 'project-db-cgi.smhrd.com',
    port: 3307,
    user: '2nd_pjt',
    password: '1234',
    database: '2nd_pjt',
    connectionLimit: 10
});

db.getConnection((err, conn) => {
    if (err) {
        console.error('MySQL 연결 실패:', err);
    } else {
        console.log('MySQL 연결 성공');
        conn.release();
    }
});

module.exports = db;