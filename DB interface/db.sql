show databases;
create database Second_PJT;
use Second_PJT;

CREATE TABLE user_info(
			user_no INT AUTO_INCREMENT PRIMARY KEY,
			login_id VARCHAR(20) NOT NULL,
			user_pwd VARCHAR(15) NOT NULL,
            user_name VARCHAR(20) NOT NULL,
            email VARCHAR(30) NOT NULL,
            gender ENUM('M', 'F'),
            age INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE user_info ADD CONSTRAINT user_info_login_id_uk UNIQUE KEY(login_id);
ALTER TABLE user_info ADD CONSTRAINT user_info_email_uk UNIQUE KEY(email);

DROP TABLE user_info;
SELECT * FROM user_info;

CREATE TABLE study_record(
	session_no INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME DEFAULT NULL,
	focus_score TINYINT CHECK (focus_score BETWEEN 0 AND 100),
    stress_score TINYINT CHECK (stress_score BETWEEN 0 AND 100)
);

ALTER TABLE study_record ADD CONSTRAINT study_record_user_no_fk FOREIGN KEY(user_no)
REFERENCES user_info(user_no);

DROP TABLE study_record;
SELECT * FROM study_record;


CREATE TABLE daily_reports (
    report_no INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT NOT NULL,
    report_date DATE NOT NULL,
    avg_focus_score DECIMAL(5,2),
    avg_stress_score DECIMAL(5,2),
    feedback_comment TEXT,
    star_rating TINYINT CHECK (star_rating BETWEEN 1 AND 5),
    content TEXT
);

ALTER TABLE daily_reports ADD CONSTRAINT daily_reports_user_no_fk FOREIGN KEY(user_no)
REFERENCES user_info(user_no);

DROP TABLE daily_reports;
SELECT * FROM daily_reports;

CREATE TABLE licence_prep (
    prepare_no INT AUTO_INCREMENT PRIMARY KEY,
    user_no INT NOT NULL,
    licence_kind VARCHAR(30) NOT NULL,
    licence_start DATETIME NOT NULL,
    licence_end DATETIME DEFAULT NULL,
    licence_feedback TEXT
);

ALTER TABLE licence_prep ADD CONSTRAINT licence_prep_user_no_fk FOREIGN KEY(user_no)
REFERENCES user_info(user_no);

DROP TABLE licence_prep;
SELECT * FROM licence_prep;