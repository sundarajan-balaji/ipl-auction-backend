package com.iplauction.backend.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record AddAuctionPlayerRequest(
        @NotNull
        Long playerId,

        @NotNull
        @Positive
        Long basePrice
) {}