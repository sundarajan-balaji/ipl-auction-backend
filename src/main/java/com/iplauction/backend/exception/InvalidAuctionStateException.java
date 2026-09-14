package com.iplauction.backend.exception;

public class InvalidAuctionStateException extends RuntimeException {

    public InvalidAuctionStateException(String message) {
        super(message);
    }
}