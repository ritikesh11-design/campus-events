-- Event Popularity (registrations per event; optional type filter)
WITH reg_counts AS (
  SELECT e.college_id, e.event_id, e.title, e.type, e.status,
         COUNT(r.student_id) AS registrations
  FROM events e
  LEFT JOIN registrations r
    ON r.college_id = e.college_id AND r.event_id = e.event_id
  WHERE e.status != 'CANCELLED'
  GROUP BY e.college_id, e.event_id
)
SELECT * FROM reg_counts
-- WHERE type = :type
ORDER BY registrations DESC, title ASC;

-- Attendance Summary for an Event
SELECT
  e.college_id, e.event_id, e.title,
  (SELECT COUNT(*) FROM registrations r WHERE r.college_id=e.college_id AND r.event_id=e.event_id) AS total_registrations,
  (SELECT COUNT(*) FROM attendance a    WHERE a.college_id=e.college_id AND a.event_id=e.event_id)   AS total_attended,
  CASE
    WHEN (SELECT COUNT(*) FROM registrations r WHERE r.college_id=e.college_id AND r.event_id=e.event_id)=0 THEN 0.0
    ELSE ROUND(100.0 * (SELECT COUNT(*) FROM attendance a WHERE a.college_id=e.college_id AND a.event_id=e.event_id) /
               (SELECT COUNT(*) FROM registrations r WHERE r.college_id=e.college_id AND r.event_id=e.event_id), 2)
  END AS attendance_pct
FROM events e
WHERE e.college_id = :college_id AND e.event_id = :event_id;

-- Average Feedback for an Event
SELECT
  college_id, event_id,
  ROUND(AVG(rating), 2) AS avg_rating,
  COUNT(*) AS num_feedback
FROM feedback
WHERE college_id = :college_id AND event_id = :event_id;

-- Student Participation (events attended by student)
SELECT
  a.college_id, a.student_id, s.name,
  COUNT(*) AS events_attended
FROM attendance a
JOIN students s USING (college_id, student_id)
WHERE a.college_id = :college_id AND a.student_id = :student_id
GROUP BY a.college_id, a.student_id;

-- Top N Most Active Students (by attendance count)
SELECT
  a.college_id, a.student_id, s.name,
  COUNT(*) AS attended_count
FROM attendance a
JOIN students s USING (college_id, student_id)
WHERE a.college_id = :college_id
GROUP BY a.college_id, a.student_id
ORDER BY attended_count DESC, s.name ASC
LIMIT :limit;
