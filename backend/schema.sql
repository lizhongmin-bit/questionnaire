CREATE DATABASE IF NOT EXISTS questionnaire CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE questionnaire;

CREATE TABLE IF NOT EXISTS surveys (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(32) DEFAULT 'draft',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS questions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  survey_id INT NOT NULL,
  title VARCHAR(500) NOT NULL,
  description VARCHAR(500),
  required TINYINT(1) DEFAULT 1,
  sort_order INT DEFAULT 0,
  CONSTRAINT fk_questions_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS options (
  id INT AUTO_INCREMENT PRIMARY KEY,
  question_id INT NOT NULL,
  text VARCHAR(255) NOT NULL,
  sort_order INT DEFAULT 0,
  CONSTRAINT fk_options_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS distribution_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  survey_id INT NOT NULL,
  real_id VARCHAR(128) NOT NULL,
  public_token VARCHAR(128) NOT NULL,
  submitted TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_survey_token (survey_id, public_token),
  CONSTRAINT fk_tokens_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS submissions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  survey_id INT NOT NULL,
  public_token VARCHAR(128) NOT NULL,
  real_id VARCHAR(128) NOT NULL,
  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip VARCHAR(64),
  user_agent VARCHAR(255),
  CONSTRAINT fk_submissions_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS answers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  submission_id INT NOT NULL,
  question_id INT NOT NULL,
  option_id INT,
  option_text VARCHAR(255),
  CONSTRAINT fk_answers_submission FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
  CONSTRAINT fk_answers_question FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
