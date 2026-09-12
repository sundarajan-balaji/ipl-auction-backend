package com.iplauction.backend.dto;

public record AuctionTeamResponse(
        Long id,
        Long auctionId,
        Long teamId,
        String teamName,
        String teamShortCode,
        Long startingPurse,
        Long remainingPurse
) {}
