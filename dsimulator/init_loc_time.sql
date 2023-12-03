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

DROP TABLE IF EXISTS src_dst;

CREATE TEMP TABLE src_dst(
	inhabitant_id INTEGER NOT NULL,
	src           INTEGER NOT NULL,
	dst           INTEGER NOT NULL,
	t_src         INTEGER NOT NULL,
	t_dst         INTEGER NOT NULL,
	              PRIMARY KEY(inhabitant_id, src, dst)
);

DROP TABLE IF EXISTS loc_time;

-- Indicate that an inhabitant arrives and leaves at a certain vertex at certain times.
CREATE TEMP TABLE loc_time(
	inhabitant_id INTEGER NOT NULL,
	vertex_id     INTEGER NOT NULL,
	arrive        INTEGER NOT NULL,
	-- This is not forced to be NOT NULL so there wouldn't be errors with unconnected graph or impossible constraints.
	leave         INTEGER,
	              PRIMARY KEY(inhabitant_id, vertex_id, arrive)
);

DROP TRIGGER IF EXISTS insert_loc_time;

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
		  SELECT inhabitant_id, end, NEW.leave + cost_min,
		         NEW.leave + cost_min + ABS(RANDOM()) % (t_dst - (NEW.leave + cost_min) + 1
		         - (SELECT MIN(d) FROM dist WHERE dist.src = end AND dist.dst = src_dst.dst))
		    FROM src_dst, edge
		   WHERE inhabitant_id = NEW.inhabitant_id
		         AND start = NEW.vertex_id
		         AND NEW.leave + cost_min +
		         (SELECT MIN(d) FROM dist WHERE dist.src = end AND dist.dst = src_dst.dst)
		         <= t_dst
		ORDER BY RANDOM()
		   LIMIT 1;
END;
