CREATE TABLE vertex(
	vertex_id INTEGER NOT NULL,
	x         REAL NOT NULL,
	y         REAL NOT NULL,
	          PRIMARY KEY(vertex_id)
);

CREATE TABLE edge(
	start       INTEGER NOT NULL,
	end         INTEGER NOT NULL,
	cost_minute INTEGER NOT NULL CHECK(cost_minute > 0),
	            PRIMARY KEY(start, end),
	            FOREIGN KEY(start) REFERENCES vertex(vertex_id),
	            FOREIGN KEY(end)   REFERENCES vertex(vertex_id)
);

INSERT INTO vertex
	WITH RECURSIVE v(vertex_id, x, y) AS (
	    SELECT 0, RANDOM() % 10, RANDOM() % 10

	     UNION ALL

	    SELECT vertex_id + 1, RANDOM() % 10, RANDOM() % 10
	      FROM v
	     LIMIT 8
	)
	SELECT vertex_id, x, y FROM v;

INSERT INTO edge
	  SELECT a.vertex_id, b.vertex_id, ABS(RANDOM()) % 4 + 1
	    FROM vertex AS a, vertex AS b
	ORDER BY RANDOM()
	   LIMIT 16;

-- Test BFS:
/*WITH RECURSIVE bfs(vertex_id) AS (
	VALUES (1)

	UNION

	SELECT end
	  FROM bfs
	       JOIN edge
	       ON vertex_id = start
)
SELECT * FROM bfs;//*/

CREATE TEMP TABLE shortest_path(
	vertex_id INTEGER NOT NULL,
	dist      INTEGER,
	visited   INTEGER NOT NULL CHECK(visited IN (0, 1)),
	          PRIMARY KEY(vertex_id),
	          FOREIGN KEY(vertex_id) REFERENCES vertex(verted_id)
);

PRAGMA recursive_triggers = ON;

-- This code is completely written by Yuxiang Lin.
-- The idea of using recursive trigger for this purpose comes from this forum post
-- https://sqlite.org/forum/info/7c89903050369164
-- though that post did not provide any implementations.
-- While there were implementations of Dijkstra in SQL online,
-- I did not base my code off them anyways as SQLite doesn't have loops
-- which were used in all these implementations.
CREATE TEMP TRIGGER update_dist AFTER UPDATE OF visited ON shortest_path
BEGIN
	UPDATE shortest_path
	   SET dist = n.d
	  FROM (SELECT end AS v, (NEW.dist + cost_minute) AS d
			  FROM edge
			 WHERE start = NEW.vertex_id) AS n
	 WHERE vertex_id = n.v AND visited = FALSE AND (dist IS NULL OR dist > n.d);

	UPDATE shortest_path
	   SET visited = TRUE
	  FROM (SELECT vertex_id
			  FROM shortest_path
			 WHERE visited = FALSE AND dist = (SELECT MIN(dist)
												 FROM shortest_path
												WHERE visited = FALSE)) AS n
	 WHERE shortest_path.vertex_id = n.vertex_id;
END;

INSERT INTO shortest_path
	WITH RECURSIVE v(vertex_id) AS (
	    SELECT 0

	     UNION ALL

	    SELECT vertex_id + 1
	      FROM v
	     LIMIT 8
	)
	SELECT vertex_id, NULL, FALSE FROM v;

UPDATE shortest_path SET dist = 0, visited = TRUE WHERE vertex_id = 0;
