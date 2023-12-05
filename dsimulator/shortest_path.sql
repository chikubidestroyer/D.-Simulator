/*
Multi-source shortest path using Dijkstra implemented as recursive trigger.
This is not implemented with a recursive CTE, which does not modification of the data.
However, is it necessary for the Dijkstra algorithm to update the label indicating
where a vertex is in the "visited" set.

Although Dijkstra is not invented by him, this code is completely written by Yuxiang Lin.
The idea of using recursive trigger for this purpose comes from this forum post:
https://sqlite.org/forum/info/7c89903050369164
However, that post did not provide any implementations.
While there were implementations of Dijkstra in SQL online,
I did not base my code off them anyways as SQLite doesn't have loops
which were used in all these implementations.

*/

PRAGMA recursive_triggers = ON; -- Need to turn this on manually.

-- Note: The default SQLITE_MAX_TRIGGER_DEPTH is just 1000,
-- so it might be necessary to increase this from the Python API.

DROP TABLE IF EXISTS dist;

CREATE TEMP TABLE dist(
	src     INTEGER NOT NULL,
	dst     INTEGER NOT NULL,
	d       INTEGER,
	visited INTEGER NOT NULL CHECK(visited IN (0, 1)),
	        PRIMARY KEY(src, dst)
);

CREATE INDEX idx_dist ON dist(src, visited, d);

-- Called when a vertex is added to the "visited" set.
CREATE TEMP TRIGGER update_dist AFTER UPDATE OF visited ON dist
BEGIN
	-- Update the shortest distance to the neighbor of this vertex.
	UPDATE dist
	   SET d = nd
	  FROM (SELECT end AS nv, (NEW.d + cost_min) AS nd
	          FROM modified_edge
	         WHERE start = NEW.dst)
	 WHERE src = NEW.src AND dst = nv AND visited = FALSE AND (d IS NULL OR d > nd);

	-- Add the closest vertex that has not been visited into the "visited" set.
	UPDATE dist
	   SET visited = TRUE
	 WHERE src = NEW.src AND visited = FALSE
	       AND d = (SELECT MIN(d) FROM dist WHERE visited = FALSE);
END;

-- Initialize the table with NULL distances.
INSERT INTO dist
	SELECT a.vertex_id, b.vertex_id, NULL, FALSE
	  FROM vertex AS a, vertex AS b;

-- Set the distance from each vertex to itself to be 0 and initiate the recursive trigger.
UPDATE dist
   SET d = 0, visited = TRUE
 WHERE src = dst;
