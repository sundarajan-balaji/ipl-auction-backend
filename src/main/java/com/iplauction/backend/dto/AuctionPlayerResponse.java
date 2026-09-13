package com.iplauction.backend.dto;

public record AuctionPlayerResponse(
        Long id,
        Long auctionId,
        Long playerId,
        String playerName,
        Long basePrice,
        String status,
        Long soldToAuctionTeamId,
        Long soldPrice
) {}