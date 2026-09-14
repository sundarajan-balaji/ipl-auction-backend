package com.iplauction.backend.dto;

import java.time.OffsetDateTime;

public record AuctionLiveStateResponse(
        Long auctionId,
        Long currentPlayerId,
        String currentPlayerName,
        Long basePrice,
        Long currentBid,
        Long highestBidderTeamId,
        String highestBidderTeamName,
        Long bidIncrement,
        String playerStatus,
        OffsetDateTime updatedAt
) {}