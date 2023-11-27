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

CREATE TEMP TABLE dist(
	src     INTEGER NOT NULL,
	dst     INTEGER NOT NULL,
	d       INTEGER,
	visited INTEGER NOT NULL CHECK(visited IN (0, 1)),
	        PRIMARY KEY(src, dst)
);

PRAGMA recursive_triggers = ON;

-- This code is completely written by Yuxiang Lin.
-- The idea of using recursive trigger for this purpose comes from this forum post
-- https://sqlite.org/forum/info/7c89903050369164
-- though that post did not provide any implementations.
-- While there were implementations of Dijkstra in SQL online,
-- I did not base my code off them anyways as SQLite doesn't have loops
-- which were used in all these implementations.

CREATE TEMP TRIGGER update_dist AFTER UPDATE OF visited ON dist
BEGIN
	UPDATE dist
	   SET d = nd
	  FROM (SELECT end AS nv, (NEW.d + cost_minute) AS nd
	          FROM edge
	         WHERE start = NEW.dst)
	 WHERE src = NEW.src AND dst = nv AND visited = FALSE AND (d IS NULL OR d > nd);

	UPDATE dist
	   SET visited = TRUE
	  FROM (SELECT dst AS ndst
	          FROM dist
	         WHERE src = NEW.src AND visited = FALSE AND d = (SELECT MIN(d)
	                                                            FROM dist
	                                                           WHERE visited = FALSE))
	 WHERE src = NEW.src AND dst = ndst;
END;

INSERT INTO dist
	SELECT a.vertex_id, b.vertex_id, NULL, FALSE
	  FROM vertex AS a, vertex AS b;

UPDATE dist
   SET d = 0, visited = TRUE
 WHERE src = dst;

-- CREATE TEMP TABLE src_dst(
--     inhabitant_id INTEGER NOT NULL,
--     src           INTEGER NOT NULL,
--     dst           INTEGER NOT NULL,
--     t_src         INTEGER NOT NULL,
--     t_dst         INTEGER NOT NULL
--                   PRIMARY KEY(inhabitant_id)
-- );

-- CREATE TEMP TABLE loc_time(
--     inhabitant_id INTEGER NOT NULL,
--     vertex_id     INTEGER NOT NULL,
--     arrive        INTEGER NOT NULL,
--     leave         INTEGER,
--               PRIMARY KEY(inhabitant_id, vertex_id, arrive),
-- );

-- INSERT INTO loc_time
--     WITH RECURSIVE lt(vertex_id, arrive, leave) AS (
--         SELECT inhabitant_id, src, 0,
--                ABS(RANDOM()) % (SELECT MIN(dist)
--                                   FROM dist
--                                  WHERE vertex_id = )
--           FROM src_dst
--     )
--     SELECT vertex_id, arraive, leave FROM loc_time
