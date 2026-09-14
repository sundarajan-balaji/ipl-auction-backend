--liquibase formatted sql

--changeset ipl-auction:017-add-auction-player-order

ALTER TABLE auction_players
    ADD COLUMN auction_order INTEGER;

CREATE UNIQUE INDEX uq_auction_players_auction_order
    ON auction_players (auction_id, auction_order);