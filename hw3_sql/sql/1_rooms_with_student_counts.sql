SELECT
    r.name,
    COUNT(s.id) AS number_of_students
FROM rooms r
LEFT JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY number_of_students DESC;