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

-- Generate vertices at random positions for testing.
INSERT INTO vertex
	WITH RECURSIVE v(vertex_id, x, y) AS (
	    SELECT 0, RANDOM() % 10, RANDOM() % 10

	     UNION ALL

	    SELECT vertex_id + 1, RANDOM() % 10, RANDOM() % 10
	      FROM v
	     LIMIT 8 -- The number of vertices.
	)
	SELECT * FROM v;

-- Generate randoms edges for testing.
-- It does not guarantee that the graph is connected or bidirectional.
INSERT INTO edge
	  SELECT a.vertex_id, b.vertex_id, ABS(RANDOM()) % 4 + 1
	    FROM vertex AS a, vertex AS b
	ORDER BY RANDOM()
	   LIMIT 20; -- The number of edges.

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

CREATE TEMP TABLE dist(
	src     INTEGER NOT NULL,
	dst     INTEGER NOT NULL,
	d       INTEGER,
	visited INTEGER NOT NULL CHECK(visited IN (0, 1)),
	        PRIMARY KEY(src, dst)
);

-- Called when a vertex is added to the "visited" set.
CREATE TEMP TRIGGER update_dist AFTER UPDATE OF visited ON dist
BEGIN
	-- Update the shortest distance to the neighbor of this vertex.
	UPDATE dist
	   SET d = nd
	  FROM (SELECT end AS nv, (NEW.d + cost_minute) AS nd
	          FROM edge
	         WHERE start = NEW.dst)
	 WHERE src = NEW.src AND dst = nv AND visited = FALSE AND (d IS NULL OR d > nd);

	-- Add the closest vertex that has not been visited into the "visited" set.
	UPDATE dist
	   SET visited = TRUE
	  FROM (SELECT dst AS ndst
	          FROM dist
	         WHERE src = NEW.src AND visited = FALSE AND d = (SELECT MIN(d) FROM dist WHERE visited = FALSE))
	 WHERE src = NEW.src AND dst = ndst;
END;

-- Initialize the table with NULL distances.
INSERT INTO dist
	SELECT a.vertex_id, b.vertex_id, NULL, FALSE
	  FROM vertex AS a, vertex AS b;

-- Set the distance from each vertex to itself to be 0 and initiate the recursive trigger.
UPDATE dist
   SET d = 0, visited = TRUE
 WHERE src = dst;

/*
Inhabitant random path generation algorithm via recursive trigger.
Given the time that the inhabitant MAY leave the source vertex (e.g. get up at home)
and the time that the inhabitant MUST arrive at the destination vertex (e.g. class begins at school),
find a random path that satisfies this time constraint and stops for random durations
in the vertices in between (including the source and the destination).

It it very hard to implement in recursive CTE due to the difficulty of RANDOMLY
selecting a SINGLE edge in each step.
(Note that you cannot use LIMIT as it behaves differently in recursive CTE.)

The constraints should be added into the src_dst first.
*/

CREATE TEMP TABLE src_dst(
	inhabitant_id INTEGER NOT NULL,
	src           INTEGER NOT NULL,
	dst           INTEGER NOT NULL,
	t_src         INTEGER NOT NULL,
	t_dst         INTEGER NOT NULL,
	              PRIMARY KEY(inhabitant_id)
);

INSERT INTO src_dst VALUES (0, 0, 1, 0, 10), (1, 1, 2, 10, 20), (2, 2, 3, 0, 20);

-- Indicate that an inhabitant arrives and leaves at a certain vertex at certain times.
CREATE TEMP TABLE loc_time(
	inhabitant_id INTEGER NOT NULL,
	vertex_id     INTEGER NOT NULL,
	arrive        INTEGER NOT NULL,
	-- This is not forced to be NOT NULL so there wouldn't be errors with unconnected graph or impossible constraints.
	leave         INTEGER,
	              PRIMARY KEY(inhabitant_id, vertex_id, arrive)
);

-- Called each time a new location-time decision is made and thus inserted into the table.
CREATE TEMP TRIGGER insert_loc_time AFTER INSERT ON loc_time
WHEN
	-- Stop when the destination is reached.
	NEW.vertex_id <> (SELECT MIN(dst) FROM src_dst WHERE inhabitant_id = NEW.inhabitant_id)
BEGIN
	-- Traverse one edge and wait at the neighboring vertex for a random amount of time,
	-- such that the current time, plus the time to traverse the edge,
	-- plus the shortest time to go from the neighboring vertex to the destination,
	-- and plus the random waiting time does not exceed the constraint.
	-- Then randomly choose one plausible edge to go through.
	INSERT INTO loc_time
		  SELECT inhabitant_id, end, NEW.leave + cost_minute,
		         NEW.leave + cost_minute + ABS(RANDOM()) % (t_dst - (NEW.leave + cost_minute) + 1
		         - (SELECT MIN(d) FROM dist WHERE dist.src = end AND dist.dst = src_dst.dst))
		    FROM src_dst, edge
		   WHERE inhabitant_id = NEW.inhabitant_id
		         AND start = NEW.vertex_id
		         AND NEW.leave + cost_minute +
		         (SELECT MIN(d) FROM dist WHERE dist.src = end AND dist.dst = src_dst.dst)
		         <= t_dst
		ORDER BY RANDOM()
		   LIMIT 1;
END;

-- Wait randomly at the source vertices and initiate the recursive trigger.
INSERT INTO loc_time
	SELECT inhabitant_id, src, t_src,
	       t_src + ABS(RANDOM()) % (t_dst - t_src + 1
	       - (SELECT MIN(d) FROM dist WHERE dist.src = src_dst.src AND dist.dst = src_dst.dst))
	  FROM src_dst;
