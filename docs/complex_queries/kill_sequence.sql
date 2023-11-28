-- uses temp table loct_time from path.sql
-- this version is NOT TESTED

CREATE TEMP table weighed_pot_victim (
  inhabitant_id INTEGER,
  description TEXT,
  chara_weight INTEGER
);

INSERT INTO weighed_pot_victim
WITH pot_victim AS (
	SELECT DISTINCT B.inhabitant_id
  	FROM status, loc_time AS A, loc_time AS B
  	WHERE A.inhabitant_id = status.killer_inhabitant_id AND
  			A.vertex = B.vertex AND
  			A.arrive <= B.leave AND
  			A.leave >= B.arrive
),
killer_info AS (
	SELECT inhabitant.* FROM status, inhabitant
  	WHERE status.killer_inhabitant_id = inhabitant.inhabitant_id
)
SELECT inhabitant_id, description, chara_weight
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
        ELSE EXISTS(
        	SELECT * FROM relationship
          	WHERE subject_id = killer_inhabitant_id AND
          		object_id = inhabitant_id AND
          		relationship.description = "mother"
        );

SELECT inhabitant_id
FROM (SELECT inhabitant_id, sum(chara_weight) AS weight_sum
	FROM weighed_pot_victim
	GROUP BY inhabitant_id) AS sub
ORDER BY weight_sum;

        