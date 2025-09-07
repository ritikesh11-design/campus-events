PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS colleges (
  college_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT NOT NULL,
  code         TEXT NOT NULL UNIQUE,
  created_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS students (
  college_id   INTEGER NOT NULL,
  student_id   INTEGER NOT NULL,
  name         TEXT NOT NULL,
  email        TEXT NOT NULL,
  roll_no      TEXT NOT NULL,
  created_at   TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (college_id, student_id),
  UNIQUE (college_id, email),
  UNIQUE (college_id, roll_no),
  FOREIGN KEY (college_id) REFERENCES colleges(college_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
  college_id   INTEGER NOT NULL,
  event_id     INTEGER NOT NULL,
  title        TEXT NOT NULL,
  type         TEXT CHECK (type IN ('Workshop','Seminar','Hackathon','Fest','Talk')) NOT NULL,
  status       TEXT CHECK (status IN ('SCHEDULED','CANCELLED','COMPLETED')) NOT NULL DEFAULT 'SCHEDULED',
  start_time   TEXT NOT NULL,
  end_time     TEXT NOT NULL,
  venue        TEXT,
  created_at   TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (college_id, event_id),
  FOREIGN KEY (college_id) REFERENCES colleges(college_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS registrations (
  college_id   INTEGER NOT NULL,
  event_id     INTEGER NOT NULL,
  student_id   INTEGER NOT NULL,
  registered_at TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (college_id, event_id, student_id),
  FOREIGN KEY (college_id, event_id) REFERENCES events(college_id, event_id) ON DELETE CASCADE,
  FOREIGN KEY (college_id, student_id) REFERENCES students(college_id, student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
  college_id   INTEGER NOT NULL,
  event_id     INTEGER NOT NULL,
  student_id   INTEGER NOT NULL,
  checkin_at   TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (college_id, event_id, student_id),
  FOREIGN KEY (college_id, event_id) REFERENCES events(college_id, event_id) ON DELETE CASCADE,
  FOREIGN KEY (college_id, student_id) REFERENCES students(college_id, student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback (
  college_id   INTEGER NOT NULL,
  event_id     INTEGER NOT NULL,
  student_id   INTEGER NOT NULL,
  rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment      TEXT,
  submitted_at TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (college_id, event_id, student_id),
  FOREIGN KEY (college_id, event_id) REFERENCES events(college_id, event_id) ON DELETE CASCADE,
  FOREIGN KEY (college_id, student_id) REFERENCES students(college_id, student_id) ON DELETE CASCADE
);
