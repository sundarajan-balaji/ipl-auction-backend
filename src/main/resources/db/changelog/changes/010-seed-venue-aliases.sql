--liquibase formatted sql

--changeset ipl-auction:010-seed-venue-aliases

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Wankhede Stadium, Mumbai', 'Mumbai'
FROM venues
WHERE name = 'Wankhede Stadium'
  AND city = 'Mumbai';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Eden Gardens, Kolkata', 'Kolkata'
FROM venues
WHERE name = 'Eden Gardens'
  AND city = 'Kolkata';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'M Chinnaswamy Stadium, Bengaluru', 'Bengaluru'
FROM venues
WHERE name = 'M Chinnaswamy Stadium'
  AND city = 'Bengaluru';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'M.Chinnaswamy Stadium', 'Bengaluru'
FROM venues
WHERE name = 'M Chinnaswamy Stadium'
  AND city = 'Bengaluru';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Feroz Shah Kotla', 'Delhi'
FROM venues
WHERE name = 'Arun Jaitley Stadium'
  AND city = 'Delhi';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Arun Jaitley Stadium, Delhi', 'Delhi'
FROM venues
WHERE name = 'Arun Jaitley Stadium'
  AND city = 'Delhi';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Rajiv Gandhi International Stadium, Uppal', 'Hyderabad'
FROM venues
WHERE name = 'Rajiv Gandhi International Stadium'
  AND city = 'Hyderabad';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Rajiv Gandhi International Stadium, Uppal, Hyderabad', 'Hyderabad'
FROM venues
WHERE name = 'Rajiv Gandhi International Stadium'
  AND city = 'Hyderabad';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'MA Chidambaram Stadium, Chepauk', 'Chennai'
FROM venues
WHERE name = 'MA Chidambaram Stadium'
  AND city = 'Chennai';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'MA Chidambaram Stadium, Chepauk, Chennai', 'Chennai'
FROM venues
WHERE name = 'MA Chidambaram Stadium'
  AND city = 'Chennai';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Sawai Mansingh Stadium, Jaipur', 'Jaipur'
FROM venues
WHERE name = 'Sawai Mansingh Stadium'
  AND city = 'Jaipur';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Narendra Modi Stadium, Ahmedabad', 'Ahmedabad'
FROM venues
WHERE name = 'Narendra Modi Stadium'
  AND city = 'Ahmedabad';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Sardar Patel Stadium, Motera', 'Ahmedabad'
FROM venues
WHERE name = 'Narendra Modi Stadium'
  AND city = 'Ahmedabad';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Punjab Cricket Association Stadium, Mohali', 'Chandigarh'
FROM venues
WHERE name = 'Punjab Cricket Association IS Bindra Stadium'
  AND city = 'Mohali';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Punjab Cricket Association IS Bindra Stadium, Mohali', 'Chandigarh'
FROM venues
WHERE name = 'Punjab Cricket Association IS Bindra Stadium'
  AND city = 'Mohali';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh', 'Chandigarh'
FROM venues
WHERE name = 'Punjab Cricket Association IS Bindra Stadium'
  AND city = 'Mohali';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Dr DY Patil Sports Academy, Mumbai', 'Mumbai'
FROM venues
WHERE name = 'Dr DY Patil Sports Academy'
  AND city = 'Navi Mumbai';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Maharashtra Cricket Association Stadium, Pune', 'Pune'
FROM venues
WHERE name = 'Maharashtra Cricket Association Stadium'
  AND city = 'Pune';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Subrata Roy Sahara Stadium', 'Pune'
FROM venues
WHERE name = 'Maharashtra Cricket Association Stadium'
  AND city = 'Pune';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Brabourne Stadium, Mumbai', 'Mumbai'
FROM venues
WHERE name = 'Brabourne Stadium'
  AND city = 'Mumbai';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Himachal Pradesh Cricket Association Stadium, Dharamsala', 'Dharamsala'
FROM venues
WHERE name = 'Himachal Pradesh Cricket Association Stadium'
  AND city = 'Dharamsala';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam', 'Visakhapatnam'
FROM venues
WHERE name = 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium'
  AND city = 'Visakhapatnam';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Zayed Cricket Stadium, Abu Dhabi', 'Abu Dhabi'
FROM venues
WHERE name = 'Sheikh Zayed Stadium'
  AND city = 'Abu Dhabi';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh', 'New Chandigarh'
FROM venues
WHERE name = 'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur'
  AND city = 'New Chandigarh';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Barsapara Cricket Stadium, Guwahati', 'Guwahati'
FROM venues
WHERE name = 'Barsapara Cricket Stadium'
  AND city = 'Guwahati';

INSERT INTO venue_aliases (
    venue_id,
    alias_name,
    alias_city
)
SELECT id, 'Shaheed Veer Narayan Singh International Stadium, Raipur', 'Raipur'
FROM venues
WHERE name = 'Shaheed Veer Narayan Singh International Stadium'
  AND city = 'Raipur';