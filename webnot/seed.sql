INSERT INTO colleges (name, code) VALUES
('Acharya Institute of Technology', 'AIT'),
('Tech Valley College', 'TVC');

INSERT INTO students (college_id, student_id, name, email, roll_no) VALUES
(1, 1, 'Riya Sen', 'riya.sen@ait.edu', 'AIT2025CS001'),
(1, 2, 'Arjun Mehta', 'arjun.mehta@ait.edu', 'AIT2025CS002'),
(2, 1, 'Meera Iyer', 'meera.iyer@tvc.edu', 'TVC2025IT001'),
(2, 2, 'Kabir Rao', 'kabir.rao@tvc.edu', 'TVC2025IT002');

INSERT INTO events (college_id, event_id, title, type, status, start_time, end_time, venue) VALUES
(1, 101, 'Intro to Data Engineering', 'Workshop', 'SCHEDULED', '2025-09-08 09:00:00', '2025-09-08 12:00:00', 'Auditorium A'),
(1, 102, 'AI Tech Talk', 'Talk', 'SCHEDULED', '2025-09-09 14:00:00', '2025-09-09 15:30:00', 'Seminar Hall 1'),
(2, 201, 'Open Source Hackathon', 'Hackathon', 'SCHEDULED', '2025-09-10 10:00:00', '2025-09-10 22:00:00', 'Lab 3');

INSERT INTO registrations (college_id, event_id, student_id) VALUES
(1, 101, 1),
(1, 101, 2),
(1, 102, 2),
(2, 201, 1),
(2, 201, 2);

INSERT INTO attendance (college_id, event_id, student_id, checkin_at) VALUES
(1, 101, 1, '2025-09-08 09:05:00'),
(2, 201, 1, '2025-09-10 10:10:00');

INSERT INTO feedback (college_id, event_id, student_id, rating, comment) VALUES
(1, 101, 1, 5, 'Great workshop!'),
(2, 201, 1, 4, 'Fun hackathon');
