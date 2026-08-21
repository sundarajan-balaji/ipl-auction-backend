--liquibase formatted sql

--changeset ipl-auction:001-create-users

CREATE TABLE users (
                       id UUID PRIMARY KEY,
                       google_subject VARCHAR(255) UNIQUE,
                       email VARCHAR(320) NOT NULL UNIQUE,
                       display_name VARCHAR(255) NOT NULL,
                       avatar_url TEXT,
                       created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);