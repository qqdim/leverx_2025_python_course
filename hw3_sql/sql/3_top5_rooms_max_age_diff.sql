SELECT
    r.name,
    (MAX(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE())) - MIN(TIMESTAMPDIFF(YEAR, s.birthday, CURDATE()))) AS age_difference
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
HAVING COUNT(s.id) > 1
ORDER BY age_difference DESC
LIMIT 5;