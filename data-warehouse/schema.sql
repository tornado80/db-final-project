CREATE DATABASE data_warehouse;

\c data_warehouse

CREATE TYPE OPERATION_TYPE AS ENUM ('INSERT', 'DELETE', 'UPDATE');

/* TABLE_NAME is changed for every tables which is logged */

CREATE TABLE history_TABLE_NAME (
    id SERIAL INT PRIMARY KEY,
    operation_timestamp TIMESTAMP,
    reason TEXT,
    type OPERATION_TYPE
);

CREATE TABLE history_old_primary_key_TABLE_NAME ( /* only primary key attributes */
    history_id INT PRIMARY KEY REFERENCES history_TABLE_NAME(id),
    primary_key_atrribute_1 attribute_1_type,
    ...
    primary_key_atrribute_j attribute_j_type,
    ...
    primary_key_atrribute_n attribute_n_type
);

CREATE TABLE history_new_value_TABLE_NAME ( /* all attributes */
    history_id INT PRIMARY KEY REFERENCES history_TABLE_NAME(id),
    atrribute_1 attribute_1_type,
    ...
    atrribute_j attribute_j_type,
    ...
    atrribute_m attribute_m_type
);

CREATE FUNCTION process_TABLE_NAME_logger() RETURNS TRIGGER AS $TABLE_NAME_logger$
    BEGIN
        INSERT INTO history_TABLE_NAME(operation_timestamp, type)
        VALUES (now(), TG_OP) RETURNING id INTO row_id;
        IF (TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN
            INSERT INTO history_old_primary_key_TABLE_NAME(history_id, primary_key_atrribute_1, ..., primary_key_atrribute_n)
            VALUES (row_id, OLD.atrribute_1, ..., OLD.atrribute_n);
        ENDIF;
        IF (TG_OP = 'UPDATE' OR TG_OP = 'INSERT') THEN
            INSERT INTO history_new_value_TABLE_NAME(history_id, atrribute_1, ..., atrribute_m)
            VALUES (row_id, NEW.atrribute_1, ..., NEW.atrribute_m);
        ENDIF;
        RETURN NULL;
    END;
$TABLE_NAME_logger$ LANGUAGE plpgsql;

CREATE TRIGGER TABLE_NAME_logger
AFTER INSERT OR UPDATE OR DELETE ON TABLE_NAME
FOR EACH ROW EXECUTE PROCEDURE process_TABLE_NAME_logger();
