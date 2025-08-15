SELECT
    r.name
FROM rooms r
JOIN students s ON r.id = s.room_id
GROUP BY r.id, r.name
HAVING COUNT(DISTINCT s.sex) > 1;