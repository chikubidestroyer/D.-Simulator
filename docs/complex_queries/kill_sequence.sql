-- uses temp table loct_time from path.sql
-- this version is NOT TESTED

DROP TEMP TABLE IF EXISTS weighed_pot_victim;
CREATE TEMP table weighed_pot_victim (
  inhabitant_id INTEGER,
  description TEXT,
  chara_weight INTEGER, 
  vertex_id INTEGER,
);

DROP TEMP TABLE IF EXISTS pot_victim;
CREATE TEMP TABLE pot_victim(
    inhabitant_id INTEGER,
    vertex_id INTEGER,
    start_min INTEGER,
    end_min INTEGER
)

INSERT INTO pot_victim
SELECT DISTINCT B.inhabitant_id, B.vertex_id, MAX(A.arrive, B.arrive), MIN(A.leave, B.leave)
FROM status, loc_time AS A, loc_time AS B
WHERE A.inhabitant_id = status.killer_inhabitant_id AND
  		A.vertex_id = B.vertex_id AND
  		A.arrive <= B.leave AND
		A.leave >= B.arrive


INSERT INTO weighed_pot_victim
WITH killer_info AS (
	SELECT inhabitant.* FROM status, inhabitant
  	WHERE status.killer_inhabitant_id = inhabitant.inhabitant_id
)
SELECT inhabitant_id, description, chara_weight, vertex_id
FROM pot_victim NATURAL JOIN inhabitant AS i NATURAL JOIN home AS h NATURAL JOIN workplace, 
	killer_chara AS k, status
WHERE status.killer_id = k.killer_id AND
	CASE
		WHEN k.description = "low income" THEN income_level = "low income"
        WHEN k.description = "high income" THEN income_level = "high income"
        WHEN k.description = "neighbor" THEN EXISTS(
          	SELECT * FROM killer_info
          	WHERE h.home_building_id = killer_info.home_building_id
        )
        WHEN k.description = "rapist" THEN EXiSTS(
          	SELECT * FROM killer_info
          	WHERE killer_info.gender <> i.gender
        )
		WHEN k.description = "colleague" THEN EXISTS(
			SELECT * FROM killer_info WHERE killer_info.workplace_id = i.workplace_id
		)
        ELSE EXISTS(
        	SELECT * FROM relationship
          	WHERE subject_id = killer_inhabitant_id AND
          		object_id = inhabitant_id AND
          		relationship.description = "Relative"
        );

SELECT inhabitant_id, vertex_id AS scene_vertex_id, (ABS(RANDOM())%(end_min-start_min) + start_min) AS min_of_death
FROM (SELECT inhabitant_id, vertex_id, sum(chara_weight) AS weight_sum
	FROM weighed_pot_victim
	GROUP BY inhabitant_id, vertex_id) AS sub, pot_victim
WHERE sub.inhabitant_id = pot_victim.inhabitant_id AND
        sub.vertex_id = pot_victim.vertex_id
ORDER BY weight_sum DESC;

        
