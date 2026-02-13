const mysql = require("mysql2");

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

db.getConnection((err, connection)=>{
    if (err) {
        console.log("db connection error", err.message);
        return;
    }
    console.log("db connection success");
    connection.release(); 
});

module.exports = db;
