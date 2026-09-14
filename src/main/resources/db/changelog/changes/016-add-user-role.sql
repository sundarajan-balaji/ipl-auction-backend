--liquibase formatted sql
--changeset ipl-auction:016-add-user-role

ALTER TABLE users
    ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'VIEWER';

ALTER TABLE users
    ADD CONSTRAINT chk_users_role
        CHECK (role IN ('ADMIN', 'AUCTIONEER', 'TEAM_USER', 'VIEWER'));