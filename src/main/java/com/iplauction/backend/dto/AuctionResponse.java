package com.iplauction.backend.dto;

public record AuctionResponse(
        Long id,
        String name,
        String season,
        String status,
        Long startingPurse
) {}