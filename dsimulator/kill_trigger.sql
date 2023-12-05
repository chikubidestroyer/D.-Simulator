
CREATE TRIGGER AFTER INSERT ON victim
BEGIN
    UPDATE inhabitant SET dead = 1 WHERE inhabitant_id = NEW.victim_id;
END;
