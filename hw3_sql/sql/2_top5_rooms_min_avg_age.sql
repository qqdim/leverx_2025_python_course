SELECT
    r.name,
    AVG(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) AS avg_age
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
ORDER BY avg_age ASC
LIMIT 5;