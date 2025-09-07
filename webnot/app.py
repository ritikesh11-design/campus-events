from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, conint
import sqlite3
from typing import Optional

DB_PATH = "../db/app.db"

app = FastAPI(title="Campus Event Reporting API", version="1.0.0")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

class CollegeIn(BaseModel):
    name: str
    code: str

class StudentIn(BaseModel):
    college_id: int
    student_id: int
    name: str
    email: str
    roll_no: str

class EventIn(BaseModel):
    college_id: int
    event_id: int
    title: str
    type: str = Field(pattern="^(Workshop|Seminar|Hackathon|Fest|Talk)$")
    status: str = Field(default="SCHEDULED", pattern="^(SCHEDULED|CANCELLED|COMPLETED)$")
    start_time: str
    end_time: str
    venue: Optional[str] = None

class RegistrationIn(BaseModel):
    college_id: int
    event_id: int
    student_id: int

class AttendanceIn(BaseModel):
    college_id: int
    event_id: int
    student_id: int

class FeedbackIn(BaseModel):
    college_id: int
    event_id: int
    student_id: int
    rating: conint(ge=1, le=5)
    comment: Optional[str] = None

def insert(sql: str, params: tuple):
    with get_db() as conn:
        try:
            conn.execute(sql, params)
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=409, detail=str(e))

def fetchall(sql: str, params: tuple = ()):
    with get_db() as conn:
        cur = conn.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
    return rows

def fetchone(sql: str, params: tuple = ()):
    with get_db() as conn:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
    return dict(row) if row else None

def event_status(college_id: int, event_id: int):
    row = fetchone("SELECT status FROM events WHERE college_id=? AND event_id=?", (college_id, event_id))
    return row["status"] if row else None

@app.post("/api/v1/colleges")
def create_college(payload: CollegeIn):
    insert("INSERT INTO colleges (name, code) VALUES (?,?)", (payload.name, payload.code))
    return {"message": "college created"}

@app.post("/api/v1/students")
def create_student(payload: StudentIn):
    insert("""INSERT INTO students (college_id, student_id, name, email, roll_no)
              VALUES (?,?,?,?,?)""", (payload.college_id, payload.student_id, payload.name, payload.email, payload.roll_no))
    return {"message": "student created"}

@app.post("/api/v1/events")
def create_event(payload: EventIn):
    insert("""INSERT INTO events (college_id, event_id, title, type, status, start_time, end_time, venue)
              VALUES (?,?,?,?,?,?,?,?)""",
           (payload.college_id, payload.event_id, payload.title, payload.type, payload.status,
            payload.start_time, payload.end_time, payload.venue))
    return {"message": "event created"}

@app.patch("/api/v1/events/{college_id}/{event_id}")
def update_event(college_id: int, event_id: int, status: Optional[str] = Query(None, pattern="^(SCHEDULED|CANCELLED|COMPLETED)$"),
                 venue: Optional[str] = None):
    with get_db() as conn:
        sets = []
        params = []
        if status: sets.append("status=?"); params.append(status)
        if venue:  sets.append("venue=?");  params.append(venue)
        if not sets:
            raise HTTPException(status_code=400, detail="No fields to update")
        params.extend([college_id, event_id])
        cur = conn.execute(f"UPDATE events SET {', '.join(sets)} WHERE college_id=? AND event_id=?", params)
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="event not found")
    return {"message": "event updated"}

@app.post("/api/v1/registrations")
def register_student(payload: RegistrationIn):
    st = event_status(payload.college_id, payload.event_id)
    if not st:
        raise HTTPException(status_code=404, detail="event not found")
    if st == "CANCELLED":
        raise HTTPException(status_code=422, detail="event cancelled; cannot register")
    insert("INSERT INTO registrations (college_id, event_id, student_id) VALUES (?,?,?)",
           (payload.college_id, payload.event_id, payload.student_id))
    return {"message": "registered"}

@app.post("/api/v1/attendance")
def mark_attendance(payload: AttendanceIn):
    st = event_status(payload.college_id, payload.event_id)
    if not st:
        raise HTTPException(status_code=404, detail="event not found")
    if st == "CANCELLED":
        raise HTTPException(status_code=422, detail="event cancelled; cannot mark attendance")
    insert("INSERT INTO attendance (college_id, event_id, student_id) VALUES (?,?,?)",
           (payload.college_id, payload.event_id, payload.student_id))
    return {"message": "attendance marked"}

@app.post("/api/v1/feedback")
def submit_feedback(payload: FeedbackIn):
    st = event_status(payload.college_id, payload.event_id)
    if not st:
        raise HTTPException(status_code=404, detail="event not found")
    if st == "CANCELLED":
        raise HTTPException(status_code=422, detail="event cancelled; cannot submit feedback")
    with get_db() as conn:
        conn.execute("""INSERT INTO feedback (college_id, event_id, student_id, rating, comment)
                        VALUES (?,?,?,?,?)
                        ON CONFLICT(college_id, event_id, student_id)
                        DO UPDATE SET rating=excluded.rating, comment=excluded.comment, submitted_at=datetime('now')""",
                     (payload.college_id, payload.event_id, payload.student_id, payload.rating, payload.comment))
        conn.commit()
    return {"message": "feedback saved"}

@app.get("/api/v1/reports/event-popularity")
def event_popularity(college_id: int, type: Optional[str] = Query(None, pattern="^(Workshop|Seminar|Hackathon|Fest|Talk)$")):
    sql = """
    WITH reg_counts AS (
      SELECT e.college_id, e.event_id, e.title, e.type, e.status,
             COUNT(r.student_id) AS registrations
      FROM events e
      LEFT JOIN registrations r
        ON r.college_id = e.college_id AND r.event_id = e.event_id
      WHERE e.college_id = ? AND e.status != 'CANCELLED'
      GROUP BY e.college_id, e.event_id
    )
    SELECT * FROM reg_counts
    """
    params = [college_id]
    if type:
        sql += " WHERE type = ?"
        params.append(type)
    sql += " ORDER BY registrations DESC, title ASC"
    return fetchall(sql, tuple(params))

@app.get("/api/v1/reports/attendance-summary/{college_id}/{event_id}")
def attendance_summary(college_id: int, event_id: int):
    row = fetchone("""
      SELECT
        e.college_id, e.event_id, e.title,
        (SELECT COUNT(*) FROM registrations r WHERE r.college_id=e.college_id AND r.event_id=e.event_id) AS total_registrations,
        (SELECT COUNT(*) FROM attendance a    WHERE a.college_id=e.college_id AND a.event_id=e.event_id)   AS total_attended
      FROM events e
      WHERE e.college_id=? AND e.event_id=?
    """, (college_id, event_id))
    if not row:
        raise HTTPException(status_code=404, detail="event not found")
    tr = row["total_registrations"]
    ta = row["total_attended"]
    row["attendance_pct"] = round(0.0 if tr == 0 else 100.0 * ta / tr, 2)
    return row

@app.get("/api/v1/reports/avg-feedback/{college_id}/{event_id}")
def avg_feedback(college_id: int, event_id: int):
    row = fetchone("""
      SELECT ROUND(AVG(rating), 2) AS avg_rating, COUNT(*) AS num_feedback
      FROM feedback WHERE college_id=? AND event_id=?
    """, (college_id, event_id))
    return row or {"avg_rating": None, "num_feedback": 0}

@app.get("/api/v1/reports/student-participation")
def student_participation(college_id: int, student_id: int):
    return fetchall("""
      SELECT a.college_id, a.student_id, s.name, COUNT(*) AS events_attended
      FROM attendance a
      JOIN students s USING (college_id, student_id)
      WHERE a.college_id = ? AND a.student_id = ?
      GROUP BY a.college_id, a.student_id
    """, (college_id, student_id))

@app.get("/api/v1/reports/top-active-students")
def top_active_students(college_id: int, limit: int = 3):
    return fetchall("""
      SELECT a.college_id, a.student_id, s.name, COUNT(*) AS attended_count
      FROM attendance a
      JOIN students s USING (college_id, student_id)
      WHERE a.college_id = ?
      GROUP BY a.college_id, a.student_id
      ORDER BY attended_count DESC, s.name ASC
      LIMIT ?
    """, (college_id, limit))

@app.get("/api/v1/health")
def health():
    return {"ok": True}
