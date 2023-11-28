CREATE TABLE vertex(
	vertex_id INTEGER NOT NULL,
	x         REAL NOT NULL,
	y         REAL NOT NULL,
	          PRIMARY KEY(vertex_id)
);

CREATE TABLE edge(
	start       INTEGER NOT NULL,
	end         INTEGER NOT NULL,
	cost_min    INTEGER NOT NULL CHECK(cost_min > 0),
	            PRIMARY KEY(start, end),
	            FOREIGN KEY(start) REFERENCES vertex(vertex_id),
	            FOREIGN KEY(end)   REFERENCES vertex(vertex_id)
);

CREATE TABLE building(
	building_id   INTEGER NOT NULL,
	building_name TEXT NOT NULL,
	lockdown      INTEGER DEFAULT FALSE NOT NULL CHECK(lockdown IN (FALSE, TRUE)),
	              FOREIGN KEY(building_id) REFERENCES vertex(vertex_id),
	              PRIMARY KEY(building_id)
);

CREATE TABLE income_range(
	income_level  INTEGER NOT NULL,
	low           INTEGER NOT NULL CHECK(low > 0),
	high          INTEGER,
	              PRIMARY KEY(income_level),
	              CHECK(high >= low)
);

CREATE TABLE home(
	home_building_id  INTEGER NOT NULL,
	income_level      INTEGER NOT NULL,
	                  PRIMARY KEY(home_building_id),
	                  FOREIGN KEY(home_building_id) REFERENCES building(building_id),
	                  FOREIGN KEY(income_level)     REFERENCES income_range(income_level)
);

CREATE TABLE occupation(
	occupation_id   INTEGER NOT NULL,
	occupation_name TEXT    NOT NULL,
	income          INTEGER NOT NULL CHECK(income > 0),
	arrive_min      INTEGER NOT NULL,
	leave_min       INTEGER NOT NULL,
	                PRIMARY KEY(occupation_id)
);

CREATE TABLE workplace(
	workplace_id          INTEGER NOT NULL,
	workplace_building_id INTEGER NOT NULL,
	occupation_id         INTEGER NOT NULL,
	                      UNIQUE(workplace_building_id, occupation_id),
	                      PRIMARY KEY(workplace_id),
	                      FOREIGN KEY(workplace_building_id) REFERENCES building(building_id),
	                      FOREIGN KEY(occupation_id)         REFERENCES occupation(occupation_id)
);

CREATE TABLE inhabitant(
	inhabitant_id    INTEGER NOT NULL,
	first_name       TEXT    NOT NULL,
	last_name        TEXT    NOT NULL,
	home_building_id INTEGER NOT NULL,
	loc_building_id  INTEGER NOT NULL,
	workplace_id     INTEGER DEFAULT NULL,
	custody          INTEGER DEFAULT FALSE NOT NULL CHECK(custody IN (FALSE, TRUE)),
	dead             INTEGER DEFAULT FALSE NOT NULL CHECK(dead IN (FALSE, TRUE)),
	gender           TEXT    NOT NULL CHECK(gender IN('m','f')),
	                 PRIMARY KEY(inhabitant_id),
	                 FOREIGN KEY(home_building_id) REFERENCES home(home_building_id),
	                 FOREIGN KEY(loc_building_id)  REFERENCES vertex(vertex_id),
	                 FOREIGN KEY(workplace_id)     REFERENCES workplace(workplace_id)
);

CREATE TABLE relationship(
	subject_id  INTEGER NOT NULL,
	object_id   INTEGER NOT NULL,
	description TEXT NOT NULL,
	            PRIMARY KEY(subject_id, object_id),
	            FOREIGN KEY(subject_id) REFERENCES inhabitant(inhabitant_id),
	            FOREIGN KEY(object_id)  REFERENCES inhabitant(inhabitant_id)
);

CREATE TABLE victim(
	victim_id       INTEGER NOT NULL,
	day_of_death    INTEGER NOT NULL,
	min_of_death    INTEGER NOT NULL,
	scene_vertex_id INTEGER NOT NULL,
	                PRIMARY KEY(victim_id),
	                FOREIGN KEY(victim_id)       REFERENCES inhabitant(inhabitant_id),
	                FOREIGN KEY(scene_vertex_id) REFERENCES vertex(vertex_id)
);

CREATE TABLE killer(
	killer_id INTEGER NOT NULL,
	          PRIMARY KEY(killer_id)
);

CREATE TABLE killer_chara(
	killer_id         INTEGER NOT NULL,
	chara_description TEXT NOT NULL,
	chara_weight      INTEGER NOT NULL,
	                  PRIMARY KEY(killer_id, chara_description)
	                  FOREIGN KEY(killer_id) REFERENCES killer(killer_id)
);

CREATE TABLE suspect(
	inhabitant_id INTEGER NOT NULL,
	              FOREIGN KEY(inhabitant_id) REFERENCES inhabitant(inhabitant_id)
);

CREATE TABLE status(
	single               INTEGER DEFAULT 0 NOT NULL CHECK(single = 0),
	day                  INTEGER DEFAULT 1 NOT NULL,
	resignation_day      INTEGER NOT NULL,
	killer_id            INTEGER NOT NULL,
	killer_inhabitant_id INTEGER NOT NULL,
	                     PRIMARY KEY(single),
	                     FOREIGN KEY(killer_id)            REFERENCES killer(killer_id)
	                     FOREIGN KEY(killer_inhabitant_id) REFERENCES inhabitant(inhabitant_id)
) WITHOUT ROWID;
