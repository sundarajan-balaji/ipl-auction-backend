package com.iplauction.backend.dto;

import java.time.OffsetDateTime;

public record BidResponse(
        Long id,
        Long auctionId,
        Long auctionPlayerId,
        Long auctionTeamId,
        Long amount,
        OffsetDateTime createdAt
) {}