--liquibase formatted sql

--changeset ipl-auction:020-add-bid-increment-to-auctions

ALTER TABLE auctions
    ADD COLUMN bid_increment BIGINT NOT NULL DEFAULT 5000000;

ALTER TABLE auctions
    ADD CONSTRAINT chk_auction_bid_increment
        CHECK (bid_increment > 0);