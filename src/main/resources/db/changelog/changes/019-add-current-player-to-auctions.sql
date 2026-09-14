--liquibase formatted sql

--changeset ipl-auction:019-add-current-player-to-auctions

ALTER TABLE auctions
    ADD COLUMN current_player_id BIGINT;

ALTER TABLE auctions
    ADD CONSTRAINT fk_auctions_current_player
        FOREIGN KEY (current_player_id)
            REFERENCES auction_players(id);