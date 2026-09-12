package com.iplauction.backend.dto;

import jakarta.validation.constraints.NotNull;

public record AddAuctionTeamRequest(
        @NotNull
        Long teamId
) {}