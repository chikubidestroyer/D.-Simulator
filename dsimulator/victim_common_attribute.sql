CREATE VIEW commonality AS
WITH victim_info AS(
    SELECT first_name,
	h.building_name AS home_building_name,
	w.building_name AS workplace_building_name,
	gender,
	scene_vertex_id,
	min_of_death,
	income_level
	FROM inhabitant LEFT OUTER JOIN home USING(home_building_id)
	JOIN building AS h ON h.building_id = home_building_id
	JOIN workplace USING(workplace_id)
	JOIN building AS w ON w.building_id = workplace_building_id
	, victim
    WHERE inhabitant_id = victim_id
)
SELECT attribute_name, attribute_value, COUNT(*) AS attribute_cnt
FROM (
    SELECT 'name' AS attribute_name, first_name AS attribute_value FROM victim_info
    UNION ALL
    SELECT 'home_building_name', home_building_name FROM victim_info
    UNION ALL
    SELECT 'workplace_building_name', workplace_building_name FROM victim_info
    UNION ALL
    SELECT 'gender', gender FROM victim_info
    UNION ALL
    SELECT 'scene_vertex_id', CAST(scene_vertex_id AS TEXT) FROM victim_info
    UNION ALL
    SELECT 'min_of_death', CAST(min_of_death AS TEXT) FROM victim_info
    UNION ALL
    SELECT 'income_level', CAST(income_level AS TEXT) FROM victim_info
) AS attributes
GROUP BY attribute_name, attribute_value
HAVING COUNT(*) >= 2
ORDER BY attribute_cnt DESC;
