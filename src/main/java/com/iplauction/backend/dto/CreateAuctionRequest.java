package com.iplauction.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record CreateAuctionRequest(

        @NotBlank
        String name,

        @NotBlank
        String season,

        @NotNull
        @Positive
        Long startingPurse
) {}