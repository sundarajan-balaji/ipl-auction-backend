package com.iplauction.backend.dto;

import jakarta.validation.constraints.NotNull;

public record PlaceBidRequest(

        @NotNull
        Long auctionTeamId

) {}