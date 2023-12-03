DELIMITER $

CREATE FUNCTION is_lockdown (building_id iNTEGER)
RETURNS BOOLEAN
NOT DETERMINISTIC
READS SQL DATA
BEGIN
	IF EXISTS(SELECT * FROM lockdown_building WHERE lockdown_building.building_id = building_id) THEN
		RETURN true;
	END IF;
    RETURN false;
END $

CREATE PROCEDURE find_path_with_remain_time(IN start_id INTEGER, IN end_id INTEGER, IN time_limit INTEGER)
BEGIN
	DECLARE time_remaining INTEGER DEFAULT time_limit;
    DECLARE inter_id INTEGER DEFAULT start_id;
    DECLARE outer_id INTEGER DEFAULT start_id;
    DECLARE order_count INTEGER DEFAULT 0;
    DECLARE time_cost INTEGER;
    DECLARE gen_temp INTEGER;
	DROP TEMPORARY TABLE IF EXISTS return_table;
	CREATE TEMPORARY TABLE return_table (order_id INTEGER, frm_id INTEGER, to_id INTEGER, remain_time INTEGER);
    
    -- this procedure will not oputput anything if the designation is under lockdown
    IF NOT is_lockdown(end_id) THEN
		
        -- when outer_it == end_id that means the inhabitant has reached the designation in the last move
		WHILE time_limit > 0 and outer_id <> end_id DO
        
			-- create temp table as all possible vertexes to move to from current position
            -- eliminates the possibility to return to the previous vertex from last move
            -- but circular path is still possible
			DROP TEMPORARY TABLE IF EXISTS temp;
            CREATE TEMPORARY TABLE temp LIKE edge;
            INSERT INTO temp SELECT * FROM edge WHERE `start` = outer_id and `end` <> inter_id;
            
            SET inter_id = outer_id;
            
            -- randomly choose next vertex to move to (outer_id) as well as the time needed to visit that vertex
			SET outer_id = cast(rand()*(SELECT count(*) FROM temp) AS UNSIGNED);
            SELECT `end`, cost_minute INTO outer_id, time_cost
            FROM temp
            LIMIT 1 OFFSET outer_id;
            
            
            -- if shortest path from chosen next intermediate vertex (outer_id) to designation is > remaining time limit
            -- or if chosen outer_id is in lockdown
            SELECT sum(weight) INTO gen_temp from sp_view WHERE frm_id = outer_id AND to_id = end_id;
			IF gen_temp > time_limit - time_cost OR is_lockdown(outer_id) THEN
                
                -- then use the shortest path's next vertex as next vertex to move to
                SELECT substring_index(
					substring_index(
						(SELECT shortest_path from sp_view WHERE frm_id = inter_id AND to_id = end_id),';',1
					),';',-1
				) INTO outer_id;
                
                # keep track of the change of time_cost
                SELECT cost_minute INTO time_cost
                FROM edge
                WHERE `end` = outer_id;
				
			END IF;
            
            -- Insert and set necessary values before entering next iteration
            INSERT INTO return_table VALUES (order_count, inter_id, outer_id, 0);
            SET order_count = order_count + 1;
            SET time_limit = time_limit - time_cost;
            
		END WHILE;
        
        -- set the time that the inhabitant remain in each vertex, defaulted to equal time
        -- can change later
        SELECT time_remaining/count(*) INTO time_remaining FROM return_table;
        UPDATE return_table SET remain_time = time_remaining;
        
        -- resulting table will be outputted, python shall fetch the result
        SELECT * FROM return_table;
        
	END IF;
    
END $
DELIMITER ;