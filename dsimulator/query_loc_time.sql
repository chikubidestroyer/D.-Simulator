-- More information in init_loc_time.sql

-- Wait randomly at the source vertices and initiate the recursive trigger.
INSERT INTO loc_time
	SELECT inhabitant_id, src, t_src,
	       t_src + ABS(RANDOM()) % (t_dst - t_src + 1
	       - (SELECT MIN(d) FROM dist WHERE dist.src = src_dst.src AND dist.dst = src_dst.dst))
	  FROM src_dst;
