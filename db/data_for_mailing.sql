\c dormyboba;

INSERT INTO mailing("theme", "mailing_text", "at", "academic_type_id", "institute_id", "year") VALUES
    ('Cool theme', 'Cool text', '2022-10-10 11:30:30', 3, 51, 0);

INSERT INTO dormyboba_user("user_id", "academic_type_id", "institute_id", "year") VALUES
    (1312, 3, 51, 0),
    (1313, 3, 37, 1),
    (1314, 4, 37, 0),
    (1315, 4, 37, 2),
    (1316, 6, 33, 3);