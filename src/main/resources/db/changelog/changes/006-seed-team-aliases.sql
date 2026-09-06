--liquibase formatted sql

--changeset ipl-auction:006-seed-team-aliases

INSERT INTO team_aliases (
    team_id,
    alias_name,
    valid_from_season,
    valid_to_season
)
VALUES
    (
        (SELECT id FROM teams WHERE short_code = 'DC'),
        'Delhi Daredevils',
        '2008',
        '2018'
    ),
    (
        (SELECT id FROM teams WHERE short_code = 'PBKS'),
        'Kings XI Punjab',
        '2008',
        '2020'
    ),
    (
        (SELECT id FROM teams WHERE short_code = 'RCB'),
        'Royal Challengers Bangalore',
        '2008',
        '2023'
    ),
    (
        (SELECT id FROM teams WHERE short_code = 'RPS'),
        'Rising Pune Supergiants',
        '2016',
        '2017'
    );