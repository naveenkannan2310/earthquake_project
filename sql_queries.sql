-- Top 10 strongest earthquakes
SELECT id, time, place, mag, depth 
FROM earthquakes 
ORDER BY mag DESC 
LIMIT 10;

-- Top 10 deepest earthquakes
SELECT id, time, place, depth, mag 
FROM earthquakes 
ORDER BY depth DESC 
LIMIT 10;

-- Count of earthquakes per year
SELECT YEAR(time) as earthquake_year, COUNT(*) as total_count 
FROM earthquakes 
GROUP BY earthquake_year;