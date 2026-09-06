--liquibase formatted sql

--changeset ipl-auction:005-seed-teams

INSERT INTO teams (name, short_code)
VALUES
    ('Chennai Super Kings', 'CSK'),
    ('Delhi Capitals', 'DC'),
    ('Gujarat Titans', 'GT'),
    ('Kolkata Knight Riders', 'KKR'),
    ('Lucknow Super Giants', 'LSG'),
    ('Mumbai Indians', 'MI'),
    ('Punjab Kings', 'PBKS'),
    ('Rajasthan Royals', 'RR'),
    ('Royal Challengers Bengaluru', 'RCB'),
    ('Sunrisers Hyderabad', 'SRH'),
    ('Deccan Chargers', 'DCH'),
    ('Gujarat Lions', 'GL'),
    ('Pune Warriors', 'PWI'),
    ('Rising Pune Supergiant', 'RPS'),
    ('Kochi Tuskers Kerala', 'KTK');